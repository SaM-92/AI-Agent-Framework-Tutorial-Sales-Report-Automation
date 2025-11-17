# Copyright (c) Microsoft. All rights reserved.

"""Daily Sales Stakeholder Report - Internal Communication Agent

This workflow transforms daily sales data into concise reports for stakeholders:
1. Data Analyzer - Reads CSV and calculates key metrics
2. Report Writer - Creates clear, actionable summary for Slack/Teams/Email

Use case: Automate daily sales summaries for managers, executives, and team leads.
Perfect for restaurants, retail stores, e-commerce, or any business tracking daily sales.
"""

import os
import csv
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from agent_framework import SequentialBuilder


from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.devui import serve
from agent_framework import Role, SequentialBuilder


def read_sales_csv(file_path: str) -> str:
    """Read CSV file and return structured summary of the data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        JSON string with data summary and sample rows
    """
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            return json.dumps({"error": "CSV file is empty"})
        
        # Get column names
        columns = list(rows[0].keys())
        
        # Sample first 5 and last 5 rows
        sample_rows = rows[:5] + rows[-5:] if len(rows) > 10 else rows
        
        summary = {
            "total_rows": len(rows),
            "columns": columns,
            "sample_data": sample_rows,
            "date_range": {
                "first": rows[0].get('Date', 'N/A'),
                "last": rows[-1].get('Date', 'N/A')
            }
        }
        
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read CSV: {str(e)}"})


def calculate_statistics(file_path: str) -> str:
    """Calculate key sales statistics from CSV data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        JSON string with statistics (totals, averages, top performers)
    """
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Calculate totals
        total_revenue = sum(float(row['Revenue']) for row in rows)
        total_units = sum(int(row['Units_Sold']) for row in rows)
        
        # Revenue by region
        region_revenue = {}
        for row in rows:
            region = row['Region']
            revenue = float(row['Revenue'])
            region_revenue[region] = region_revenue.get(region, 0) + revenue
        
        # Revenue by product
        product_revenue = {}
        for row in rows:
            product = row['Product']
            revenue = float(row['Revenue'])
            product_revenue[product] = product_revenue.get(product, 0) + revenue
        
        # Revenue by salesperson
        salesperson_revenue = {}
        for row in rows:
            person = row['Salesperson']
            revenue = float(row['Revenue'])
            salesperson_revenue[person] = salesperson_revenue.get(person, 0) + revenue
        
        # Find top performers
        top_region = max(region_revenue.items(), key=lambda x: x[1])
        top_product = max(product_revenue.items(), key=lambda x: x[1])
        top_salesperson = max(salesperson_revenue.items(), key=lambda x: x[1])
        
        stats = {
            "total_revenue": f"${total_revenue:,.2f}",
            "total_units_sold": total_units,
            "average_revenue_per_transaction": f"${total_revenue/len(rows):,.2f}",
            "number_of_transactions": len(rows),
            "top_region": {"name": top_region[0], "revenue": f"${top_region[1]:,.2f}"},
            "top_product": {"name": top_product[0], "revenue": f"${top_product[1]:,.2f}"},
            "top_salesperson": {"name": top_salesperson[0], "revenue": f"${top_salesperson[1]:,.2f}"},
            "region_breakdown": {k: f"${v:,.2f}" for k, v in sorted(region_revenue.items(), key=lambda x: x[1], reverse=True)},
            "product_breakdown": {k: f"${v:,.2f}" for k, v in sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)},
            "salesperson_breakdown": {k: f"${v:,.2f}" for k, v in sorted(salesperson_revenue.items(), key=lambda x: x[1], reverse=True)}
        }
        
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to calculate statistics: {str(e)}"})





async def main() -> None:
    """Main function to set up and run the Data Story Teller workflow."""
    # Load environment variables
    load_dotenv()
    
    # Create Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(
        api_key=os.getenv("API_KEY"),
        deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        api_version=os.getenv("AZURE_AI_API_VERSION")
    )
    
    # Agent 1: Data Analyzer - Reads CSV and returns structured data only
    data_analyzer = chat_client.create_agent(
        name="DataAnalyzer",
        instructions=(
            "You are a data analyst. Your job is to extract and return ONLY structured data in JSON format. "
            "Use the calculate_statistics tool to get the data, then return it as a clean JSON object. "
            "Do NOT write sentences or narratives. Do NOT interpret the data. "
            "Just return the raw statistics in JSON format so the next agent can write about it. "
            "Example output format:\n"
            "{\n"
            '  "total_revenue": "$1,070,000.00",\n'
            '  "total_transactions": 56,\n'
            '  "top_salesperson": {"name": "Mike Brown", "revenue": "$272,000"},\n'
            '  "top_product": {"name": "Product D", "revenue": "$352,000"},\n'
            '  "top_region": {"name": "East", "revenue": "$272,000"}\n'
            "}"
        ),
        tools=[read_sales_csv, calculate_statistics]
    )
    
    # Agent 2: Report Writer - Creates concise stakeholder summary from JSON data
    report_writer = chat_client.create_agent(
        name="ReportWriter",
        instructions=(
            "You are an internal business analyst writing daily sales summaries for stakeholders. "
            "You will receive structured JSON data from the previous agent. "
            "Your job is to create a clear, actionable report for Slack/Teams/Email.\n\n"
            "**REQUIRED FORMAT**:\n"
            "1. Header: Date range + quick summary line\n"
            "2. Key Metrics: 3-4 most important numbers (revenue, transactions, averages)\n"
            "3. Top Performers: Best region/product/salesperson with their numbers\n"
            "4. Brief Insight: ONE sentence about what stands out or needs attention\n\n"
            "**EXAMPLE 1 (Restaurant Context)**:\n"
            "📊 **Daily Sales Report - Nov 17, 2025**\n\n"
            "Strong Friday! Dinner rush drove solid numbers.\n\n"
            "**Key Metrics:**\n"
            "• Total Revenue: $8,450\n"
            "• Transactions: 127\n"
            "• Avg Check: $66.54\n"
            "• Units Sold: 342\n\n"
            "**Top Performers:**\n"
            "🏆 Best Location: Downtown ($3,200)\n"
            "🍕 Best Item: Margherita Pizza ($1,890 revenue)\n"
            "⭐ Top Server: Maria ($2,100 in sales)\n\n"
            "💡 *Insight: Downtown location up 18% vs last Friday. Consider staffing boost for weekends.*\n\n"
            "**EXAMPLE 2 (Retail Context)**:\n"
            "📈 **Sales Summary - October 2024**\n\n"
            "Solid month with consistent growth across regions.\n\n"
            "**Key Metrics:**\n"
            "• Total Revenue: $1,070,000\n"
            "• Transactions: 56\n"
            "• Avg Deal Size: $19,107\n"
            "• Units Moved: 5,780\n\n"
            "**Top Performers:**\n"
            "🌎 Best Region: East ($272,000)\n"
            "📦 Best Product: Product D ($352,000)\n"
            "🎯 Top Rep: Mike Brown ($272,000)\n\n"
            "💡 *Insight: Product D momentum continues - up 22% MoM. Stock levels should be reviewed.*\n\n"
            "**CRITICAL RULES**:\n"
            "- Professional but conversational tone\n"
            "- Use EXACT numbers from JSON data\n"
            "- Keep total message under 150 words\n"
            "- Include ONE actionable insight at the end\n"
            "- Use minimal emojis (just for section headers and highlights)\n"
            "- Format for readability in Slack/Teams (bold headers, bullet points)\n"
            "- NO fluff or unnecessary commentary\n\n"
            "**Adapt context based on data** (restaurant, retail, e-commerce, etc.)"
        )
    )
    
    # Build the workflow: Analyzer → Report Writer
    workflow = SequentialBuilder().participants([data_analyzer, report_writer]).build()
    
    # Wrap as agent and run
    agent = workflow.as_agent(name="DailySalesReporter")
    prompt = "Analyze sample_sales_data.csv and create a daily sales summary report for stakeholders."
    agent_response = await agent.run(prompt)

    if agent_response.messages:
        print("\n===== Conversation =====")
        for i, msg in enumerate(agent_response.messages, start=1):
            role_value = getattr(msg.role, "value", msg.role)
            normalized_role = str(role_value).lower() if role_value is not None else "assistant"
            name = msg.author_name or ("assistant" if normalized_role == Role.ASSISTANT.value else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
