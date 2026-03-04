"""Test script to verify select_strike logic for sell put strategy."""

import sys
sys.path.insert(0, '/mnt/harddisk/lwb/options-trading-platform')

from core.backtesting.strategies.sell_put import SellPutStrategy
from core.backtesting.pricing import OptionsPricer

def test_put_delta_search():
    """Verify that the binary search finds correct strike for puts."""
    
    print("\n" + "="*70)
    print("Testing Put Option Strike Selection")
    print("="*70)
    
    underlying_price = 150.0
    iv = 0.30
    T = 30 / 365.0  # 30 days
    target_delta = -0.30
    
    print(f"\nUnderlying price: ${underlying_price}")
    print(f"Target delta: {target_delta}")
    print(f"IV: {iv*100}%")
    print(f"DTE: {int(T*365)} days")
    
    # Test the select_strike method
    params = {
        "symbol": "AAPL",
        "delta_target": 0.30,  # Absolute value
        "dte_min": 30,
        "dte_max": 30,
    }
    
    strategy = SellPutStrategy(params)
    selected_strike = strategy.select_strike(underlying_price, iv, T, "P")
    
    print(f"\nSelected strike: ${selected_strike}")
    
    # Verify the delta at selected strike
    actual_delta = OptionsPricer.delta(underlying_price, selected_strike, T, iv, "P")
    print(f"Actual delta at selected strike: {actual_delta:.4f}")
    print(f"Delta difference from target: {abs(actual_delta - target_delta):.4f}")
    
    # Test a range of strikes to show the relationship
    print("\n" + "-"*70)
    print("Strike vs Delta relationship:")
    print("-"*70)
    
    test_strikes = [
        underlying_price * 0.85,  # Deep OTM
        underlying_price * 0.90,  # OTM
        underlying_price * 0.95,  # Slightly OTM
        underlying_price * 1.00,  # ATM
        underlying_price * 1.05,  # Slightly ITM
        underlying_price * 1.10,  # ITM
    ]
    
    for strike in test_strikes:
        delta = OptionsPricer.delta(underlying_price, strike, T, iv, "P")
        distance = (strike - underlying_price) / underlying_price * 100
        marker = " <-- SELECTED" if abs(strike - selected_strike) < 0.5 else ""
        print(f"Strike ${strike:7.2f} ({distance:+6.1f}%): Delta = {delta:7.4f}{marker}")
    
    # Verify correctness
    delta_diff = abs(actual_delta - target_delta)
    print("\n" + "="*70)
    if delta_diff < 0.05:  # Within 5% tolerance
        print(f"✅ PASS: Selected strike is close to target delta!")
        print(f"   Delta difference: {delta_diff:.4f} (< 0.05)")
    else:
        print(f"❌ FAIL: Selected strike is NOT close to target delta!")
        print(f"   Delta difference: {delta_diff:.4f} (>= 0.05)")
        print(f"\nThis indicates a problem with the binary search logic!")
    print("="*70)
    
    return delta_diff < 0.05


def test_call_delta_search():
    """Verify that the binary search finds correct strike for calls."""
    
    print("\n" + "="*70)
    print("Testing Call Option Strike Selection")
    print("="*70)
    
    underlying_price = 150.0
    iv = 0.30
    T = 30 / 365.0
    target_delta = 0.30
    
    print(f"\nUnderlying price: ${underlying_price}")
    print(f"Target delta: {target_delta}")
    print(f"IV: {iv*100}%")
    print(f"DTE: {int(T*365)} days")
    
    params = {
        "symbol": "AAPL",
        "delta_target": 0.30,
        "dte_min": 30,
        "dte_max": 30,
    }
    
    strategy = SellPutStrategy(params)
    selected_strike = strategy.select_strike(underlying_price, iv, T, "C")
    
    print(f"\nSelected strike: ${selected_strike}")
    
    actual_delta = OptionsPricer.delta(underlying_price, selected_strike, T, iv, "C")
    print(f"Actual delta at selected strike: {actual_delta:.4f}")
    print(f"Delta difference from target: {abs(actual_delta - target_delta):.4f}")
    
    # Verify correctness
    delta_diff = abs(actual_delta - target_delta)
    print("\n" + "="*70)
    if delta_diff < 0.05:
        print(f"✅ PASS: Selected strike is close to target delta!")
        print(f"   Delta difference: {delta_diff:.4f} (< 0.05)")
    else:
        print(f"❌ FAIL: Selected strike is NOT close to target delta!")
        print(f"   Delta difference: {delta_diff:.4f} (>= 0.05)")
    print("="*70)
    
    return delta_diff < 0.05


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SELECT_STRIKE BINARY SEARCH VERIFICATION")
    print("="*70)
    
    put_pass = test_put_delta_search()
    call_pass = test_call_delta_search()
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Put Option Test:  {'✅ PASS' if put_pass else '❌ FAIL'}")
    print(f"Call Option Test: {'✅ PASS' if call_pass else '❌ FAIL'}")
    
    if put_pass and call_pass:
        print("\n🎉 All tests passed! The select_strike logic is correct.")
    elif put_pass and not call_pass:
        print("\n⚠️  Warning: Call option selection may have issues.")
    elif not put_pass and call_pass:
        print("\n⚠️  Warning: Put option selection may have issues.")
    else:
        print("\n❌ Both put and call selection have issues!")
    
    print("="*70 + "\n")
