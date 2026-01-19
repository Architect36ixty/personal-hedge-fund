#!/usr/bin/env python3
"""
Manual agent runner - Execute agents immediately for testing
"""
import sys
from dotenv import load_dotenv
load_dotenv()

from agents.crypto.scout import run as run_crypto_scout
from agents.stocks.scout import run as run_stock_scout
from agents.coach import run as run_coach

def main():
    print("🚀 Starting Manual Agent Execution...")
    
    if len(sys.argv) > 1:
        agent = sys.argv[1].lower()
        if agent == 'crypto':
            print("\n📊 Running Crypto Scout...")
            run_crypto_scout()
        elif agent == 'stock':
            print("\n📈 Running Stock Scout...")
            run_stock_scout()
        elif agent == 'coach':
            print("\n🤖 Running Coach...")
            run_coach()
        else:
            print(f"Unknown agent: {agent}")
            print("Available agents: crypto, stock, coach")
    else:
        print("\n📊 Running Crypto Scout...")
        run_crypto_scout()
        
        print("\n📈 Running Stock Scout...")
        run_stock_scout()
        
        print("\n🤖 Running Coach...")
        run_coach()
    
    print("\n✅ Agent execution complete!")

if __name__ == "__main__":
    main()
