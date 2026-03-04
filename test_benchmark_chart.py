"""Test script to verify benchmark comparison chart fix."""

from app.components.charts import create_pnl_chart
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_benchmark():
    """Test chart with single benchmark."""
    print("\n" + "="*60)
    print("Test 1: Single Benchmark Comparison")
    print("="*60)
    
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    pnl_values = [0, 100, 150, 200, 250]
    
    benchmark_data = {
        "SPY": [
            {"date": "2024-01-01", "cumulative_pnl": 0, "percentage_return": 0},
            {"date": "2024-01-02", "cumulative_pnl": 50, "percentage_return": 0.05},
            {"date": "2024-01-03", "cumulative_pnl": 80, "percentage_return": 0.08},
            {"date": "2024-01-04", "cumulative_pnl": 120, "percentage_return": 0.12},
            {"date": "2024-01-05", "cumulative_pnl": 150, "percentage_return": 0.15},
        ]
    }
    
    fig = create_pnl_chart(
        dates=dates,
        pnl_values=pnl_values,
        benchmark_data=benchmark_data,
        initial_capital=100000,
        title="Single Benchmark Test"
    )
    
    # Verify traces
    trace_names = [trace.name for trace in fig.data]
    print(f"Trace names: {trace_names}")
    
    assert "Strategy P&L ($)" in trace_names, "Missing strategy P&L trace"
    assert "SPY P&L ($)" in trace_names, "Missing SPY P&L trace"
    assert "SPY Return (%)" in trace_names, "Missing SPY Return trace"
    
    print("✅ Single benchmark test passed!")
    return True


def test_multiple_benchmarks():
    """Test chart with multiple benchmarks."""
    print("\n" + "="*60)
    print("Test 2: Multiple Benchmark Comparison")
    print("="*60)
    
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    pnl_values = [0, 100, 150, 200, 250]
    
    benchmark_data = {
        "SPY": [
            {"date": "2024-01-01", "cumulative_pnl": 0, "percentage_return": 0},
            {"date": "2024-01-02", "cumulative_pnl": 50, "percentage_return": 0.05},
            {"date": "2024-01-03", "cumulative_pnl": 80, "percentage_return": 0.08},
            {"date": "2024-01-04", "cumulative_pnl": 120, "percentage_return": 0.12},
            {"date": "2024-01-05", "cumulative_pnl": 150, "percentage_return": 0.15},
        ],
        "QQQ": [
            {"date": "2024-01-01", "cumulative_pnl": 0, "percentage_return": 0},
            {"date": "2024-01-02", "cumulative_pnl": 80, "percentage_return": 0.08},
            {"date": "2024-01-03", "cumulative_pnl": 130, "percentage_return": 0.13},
            {"date": "2024-01-04", "cumulative_pnl": 180, "percentage_return": 0.18},
            {"date": "2024-01-05", "cumulative_pnl": 220, "percentage_return": 0.22},
        ],
        "AAPL": [
            {"date": "2024-01-01", "cumulative_pnl": 0, "percentage_return": 0},
            {"date": "2024-01-02", "cumulative_pnl": 120, "percentage_return": 0.12},
            {"date": "2024-01-03", "cumulative_pnl": 180, "percentage_return": 0.18},
            {"date": "2024-01-04", "cumulative_pnl": 250, "percentage_return": 0.25},
            {"date": "2024-01-05", "cumulative_pnl": 300, "percentage_return": 0.30},
        ],
    }
    
    fig = create_pnl_chart(
        dates=dates,
        pnl_values=pnl_values,
        benchmark_data=benchmark_data,
        initial_capital=100000,
        title="Multiple Benchmarks Test"
    )
    
    # Verify traces
    trace_names = [trace.name for trace in fig.data]
    print(f"Trace names: {trace_names}")
    
    expected_traces = [
        "Strategy P&L ($)",
        "SPY P&L ($)", "SPY Return (%)",
        "QQQ P&L ($)", "QQQ Return (%)",
        "AAPL P&L ($)", "AAPL Return (%)",
    ]
    
    for expected in expected_traces:
        assert expected in trace_names, f"Missing expected trace: {expected}"
    
    print(f"✅ All {len(trace_names)} traces created successfully!")
    print("✅ Multiple benchmarks test passed!")
    return True


def test_empty_benchmark():
    """Test chart with empty benchmark data."""
    print("\n" + "="*60)
    print("Test 3: Empty Benchmark Data")
    print("="*60)
    
    dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
    pnl_values = [0, 100, 150]
    
    benchmark_data = {}
    
    fig = create_pnl_chart(
        dates=dates,
        pnl_values=pnl_values,
        benchmark_data=benchmark_data,
        initial_capital=100000,
        title="Empty Benchmark Test"
    )
    
    trace_names = [trace.name for trace in fig.data]
    print(f"Trace names: {trace_names}")
    
    assert len(trace_names) == 2, f"Expected 2 traces (P&L + %), got {len(trace_names)}"
    assert "Strategy P&L ($)" in trace_names
    assert "Strategy Return (%)" in trace_names
    
    print("✅ Empty benchmark test passed!")
    return True


def test_invalid_benchmark_data():
    """Test chart with invalid benchmark data structure."""
    print("\n" + "="*60)
    print("Test 4: Invalid Benchmark Data")
    print("="*60)
    
    dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
    pnl_values = [0, 100, 150]
    
    benchmark_data = {
        "INVALID": [
            {"wrong_field": "value"},  # Missing required fields
            {"date": "2024-01-02"},  # Missing cumulative_pnl
        ],
        "VALID": [
            {"date": "2024-01-01", "cumulative_pnl": 50, "percentage_return": 0.05},
            {"date": "2024-01-02", "cumulative_pnl": 80, "percentage_return": 0.08},
        ]
    }
    
    fig = create_pnl_chart(
        dates=dates,
        pnl_values=pnl_values,
        benchmark_data=benchmark_data,
        initial_capital=100000,
        title="Invalid Benchmark Test"
    )
    
    trace_names = [trace.name for trace in fig.data]
    print(f"Trace names: {trace_names}")
    
    # Should have strategy traces + valid benchmark
    assert "Strategy P&L ($)" in trace_names
    assert "VALID P&L ($)" in trace_names or "VALID Return (%)" in trace_names
    
    print("✅ Invalid benchmark data handled gracefully!")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BENCHMARK COMPARISON CHART FIX - TEST SUITE")
    print("="*70)
    
    all_passed = True
    
    try:
        all_passed &= test_single_benchmark()
        all_passed &= test_multiple_benchmarks()
        all_passed &= test_empty_benchmark()
        all_passed &= test_invalid_benchmark_data()
        
        print("\n" + "="*70)
        if all_passed:
            print("ALL TESTS PASSED! ✅")
            print("\nFixed Issues:")
            print("- Multiple benchmark curves now display correctly")
            print("- Better error handling for invalid data")
            print("- Improved logging for debugging")
            print("- Enhanced color scheme for better distinction")
        else:
            print("SOME TESTS FAILED! ❌")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
