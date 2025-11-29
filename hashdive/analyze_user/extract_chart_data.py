#!/usr/bin/env python3
"""
Script to extract and quantify Plotly chart data from user JSON files.
Extracts data from radar charts (most_traded_categories, smart_score_by_category, win_rate_by_category)
and stores them in a clean, analysis-ready format.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def extract_plotly_data(plotly_json_string: str) -> Optional[Dict[str, Any]]:
    """
    Extract data from a Plotly chart JSON string.
    
    Args:
        plotly_json_string: JSON string containing Plotly chart data
        
    Returns:
        Dictionary with extracted data or None if parsing fails
    """
    try:
        # Parse the outer JSON
        outer_data = json.loads(plotly_json_string)
        
        # Navigate to the spec field and parse it
        spec_string = outer_data['delta']['newElement']['plotlyChart']['spec']
        spec_data = json.loads(spec_string)
        
        # Extract the main data from the first trace
        trace = spec_data['data'][0]
        
        # Get theta (categories) and r (values)
        categories = trace.get('theta', [])
        values = trace.get('r', [])
        
        # Remove duplicate last element (polar charts repeat first point)
        if len(categories) > 1 and categories[0] == categories[-1]:
            categories = categories[:-1]
            values = values[:-1]
        
        # Create a dictionary mapping categories to values
        data_dict = dict(zip(categories, values))
        
        return data_dict
        
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error extracting Plotly data: {e}", file=sys.stderr)
        return None


def process_user_json(input_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Process a user JSON file and extract quantified chart data.
    
    Args:
        input_path: Path to the input JSON file
        output_path: Path to save the output JSON file (optional)
        
    Returns:
        Dictionary with extracted and quantified data
    """
    # Read the input JSON
    with open(input_path, 'r') as f:
        user_data = json.load(f)
    
    # Extract data from each chart
    charts_to_extract = [
        'most_traded_categories_chart',
        'smart_score_by_category',
        'win_rate_by_category'
    ]
    
    extracted_data = {}
    
    for chart_name in charts_to_extract:
        if chart_name in user_data:
            chart_data = extract_plotly_data(user_data[chart_name])
            if chart_data:
                # Create a clean field name
                clean_name = chart_name.replace('_chart', '').replace('_by_category', '_categories')
                extracted_data[clean_name] = chart_data
                print(f"✓ Extracted {clean_name}: {len(chart_data)} categories")
    
    # Add the extracted data to the user data
    user_data['category_metrics'] = extracted_data
    
    # Optionally remove the original chart strings to save space
    # Uncomment the following lines if you want to remove the raw chart data
    # for chart_name in charts_to_extract:
    #     if chart_name in user_data:
    #         del user_data[chart_name]
    
    # Save to output file if specified
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        print(f"\n✓ Saved processed data to: {output_path}")
    
    return user_data


def print_summary(data: Dict[str, Any]) -> None:
    """Print a summary of the extracted data."""
    print("\n" + "="*60)
    print("EXTRACTED CATEGORY METRICS SUMMARY")
    print("="*60)
    
    if 'category_metrics' not in data:
        print("No category metrics found!")
        return
    
    metrics = data['category_metrics']
    
    # Most Traded Categories
    if 'most_traded_categories' in metrics:
        print("\n📊 Most Traded Categories (Markets Count):")
        sorted_traded = sorted(metrics['most_traded_categories'].items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_traded:
            print(f"  {category:12s}: {count:6.0f} markets")
        total_markets = sum(metrics['most_traded_categories'].values())
        print(f"  {'TOTAL':12s}: {total_markets:6.0f} markets")
    
    # Smart Score by Category
    if 'smart_score_categories' in metrics:
        print("\n🧠 Smart Score by Category:")
        sorted_scores = sorted(metrics['smart_score_categories'].items(), key=lambda x: x[1], reverse=True)
        for category, score in sorted_scores:
            print(f"  {category:12s}: {score:6.2f}")
        avg_score = sum(metrics['smart_score_categories'].values()) / len(metrics['smart_score_categories'])
        print(f"  {'AVERAGE':12s}: {avg_score:6.2f}")
    
    # Win Rate by Category
    if 'win_rate_categories' in metrics:
        print("\n🎯 Win Rate by Category:")
        sorted_winrate = sorted(metrics['win_rate_categories'].items(), key=lambda x: x[1], reverse=True)
        for category, rate in sorted_winrate:
            print(f"  {category:12s}: {rate*100:5.2f}%")
        avg_winrate = sum(metrics['win_rate_categories'].values()) / len(metrics['win_rate_categories'])
        print(f"  {'AVERAGE':12s}: {avg_winrate*100:5.2f}%")
    
    print("\n" + "="*60)


def main():
    """Main function to run the script."""
    # Default test file
    default_input = Path("/Users/azuolasbalbieris/dev/dsa-polymarket/data/users/0xcb3b6ed4b431a9401171ba0b2694e2e296d8a2b6.json")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    else:
        input_path = default_input
        print(f"No input file specified, using default: {input_path}")
    
    # Check if input file exists
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        # Create output path by adding _processed suffix
        output_path = input_path.parent / f"{input_path.stem}_processed{input_path.suffix}"
    
    print(f"Processing: {input_path}")
    print(f"Output to: {output_path}")
    print("-" * 60)
    
    # Process the file
    processed_data = process_user_json(input_path, output_path)
    
    # Print summary
    print_summary(processed_data)
    
    print("\n✅ Processing complete!")


if __name__ == "__main__":
    main()

