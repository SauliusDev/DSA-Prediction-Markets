import pandas as pd
import os

from analysis import (
    plot_pnl_distribution,
    plot_winrate_distribution,
    plot_markets_distribution,
    plot_effective_count_distribution,
    plot_correlations
)

def load_data(path=None):
    if path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, 'traders.csv')
    return pd.read_csv(path)

def parse_filter(value_str):
    if not value_str or value_str.strip() == '':
        return None, None
    
    value_str = value_str.strip()
    
    if '-' in value_str and not value_str.startswith('-'):
        parts = value_str.split('-')
        if len(parts) == 2:
            try:
                return float(parts[0]), float(parts[1])
            except ValueError:
                return None, None
    
    if value_str.startswith('>'):
        try:
            return float(value_str[1:]), None
        except ValueError:
            return None, None
    
    if value_str.startswith('<'):
        try:
            return None, float(value_str[1:])
        except ValueError:
            return None, None
    
    try:
        val = float(value_str)
        return val, None
    except ValueError:
        return None, None

def apply_filter(df, column, min_val, max_val):
    if min_val is not None:
        df = df[df[column] >= min_val]
    if max_val is not None:
        df = df[df[column] <= max_val]
    return df

def main():
    df = load_data()
    print(f"\nLoaded {len(df)} traders")
    print("\n" + "="*60)
    print("SMART SCORE RANGE FILTER CLI")
    print("="*60)
    print("\nFilter syntax:")
    print("  >X     - above X (e.g., >1000)")
    print("  <X     - below X (e.g., <5000)")
    print("  X-Y    - between X and Y (e.g., 1000-5000)")
    print("  X      - above X (e.g., 1000)")
    print("  [empty]- no filter")
    print("\nNote: Win rate is 0-1 (e.g., 0.5 = 50%)")
    print("="*60)
    
    while True:
        print("\n--- New Filter ---")
        
        pnl_input = input("PnL filter (sum_pnl): ").strip()
        pnl_min, pnl_max = parse_filter(pnl_input)
        
        wr_input = input("Win Rate filter (0-1): ").strip()
        wr_min, wr_max = parse_filter(wr_input)
        
        markets_input = input("Markets filter (num_markets): ").strip()
        markets_min, markets_max = parse_filter(markets_input)
        
        filtered = df.copy()
        filtered = apply_filter(filtered, 'sum_pnl', pnl_min, pnl_max)
        filtered = apply_filter(filtered, 'win_rate', wr_min, wr_max)
        filtered = apply_filter(filtered, 'num_markets', markets_min, markets_max)
        
        print("\n" + "-"*40)
        print(f"RESULTS: {len(filtered)} traders found ({len(filtered)/len(df)*100:.1f}%)")
        print("-"*40)
        
        if len(filtered) > 0:
            print(f"  PnL:         mean=${filtered['sum_pnl'].mean():,.0f}, median=${filtered['sum_pnl'].median():,.0f}")
            print(f"  Win Rate:    mean={filtered['win_rate'].mean():.2%}, median={filtered['win_rate'].median():.2%}")
            print(f"  Markets:     mean={filtered['num_markets'].mean():.0f}, median={filtered['num_markets'].median():.0f}")
            print(f"  Smart Score: mean={filtered['score'].mean():.1f}, median={filtered['score'].median():.1f}")
            
            generate = input("\nGenerate plots? (y/n): ").strip().lower()
            if generate == 'y':
                script_dir = os.path.dirname(os.path.abspath(__file__))
                output_dir = os.path.join(script_dir, 'data')
                os.makedirs(output_dir, exist_ok=True)
                
                print("\nGenerating plots...")
                plot_pnl_distribution(filtered, save=True, path=f"{output_dir}/filtered_pnl_distribution.png")
                plot_winrate_distribution(filtered, save=True, path=f"{output_dir}/filtered_winrate_distribution.png")
                plot_markets_distribution(filtered, save=True, path=f"{output_dir}/filtered_markets_distribution.png")
                plot_effective_count_distribution(filtered, save=True, path=f"{output_dir}/filtered_effective_count_distribution.png")
                plot_correlations(filtered, save=True, path=f"{output_dir}/filtered_correlations.png")
                print(f"Plots saved to: {output_dir}/filtered_*.png")
        
        cont = input("\nFilter again? (y/n): ").strip().lower()
        if cont != 'y':
            break
    
    print("\nGoodbye!")

if __name__ == '__main__':
    main()

