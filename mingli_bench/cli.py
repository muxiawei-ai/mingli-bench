"""
Command-line interface for Fortune Telling Benchmark.
"""

import argparse
import json
import sys

from .calendar import hour_branch, parse_bazi_pillars
from .charts import extract_bazi_summary, get_chart_record, get_chart_summary
from .bazi import bazi_from_birth_info, bazi_from_gregorian
from .locations import resolve_timezone
from .models.factory import ModelFactory
from .utils import get_logger
from .data import DataLoader

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Chinese Fortune Telling Benchmark - Evaluate LLMs on Chinese fortune telling tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate GPT-4
  python -m mingli_bench.cli --model gpt-4

  # Evaluate only 2023 benchmark questions
  python -m mingli_bench.cli --model gpt-4 --year 2023
  
  # Use Chain-of-Thought reasoning
  python -m mingli_bench.cli --model gpt-4 --cot
  
  # Test with 10 sample questions
  python -m mingli_bench.cli --model claude-3-sonnet --sample 10
  
  # Filter by category
  python -m mingli_bench.cli --model gemini-pro --categories 事件 婚姻

  # Developer utilities, no model key required
  python -m mingli_bench.cli --hour-branch 23
  python -m mingli_bench.cli --analyze-pillars "甲寅 戊辰 己亥 壬申"
  python -m mingli_bench.cli --bazi-date 1974-04-28 --bazi-time 16:40
  python -m mingli_bench.cli --bazi-date 1978-04-05 --bazi-time 18:00 --bazi-location 台湾
  python -m mingli_bench.cli --bazi-case case_13
  python -m mingli_bench.cli --show-chart case_1
        """
    )
    
    # Model selection
    parser.add_argument(
        "--model", "-m",
        help="Model to evaluate (e.g., gpt-4, claude-3-sonnet, gemini-pro)"
    )
    
    # Evaluation options
    parser.add_argument(
        "--cot",
        action="store_true",
        help="Use Chain-of-Thought reasoning"
    )
    
    parser.add_argument(
        "--astro",
        action="store_true",
        help="Use astronomical/astrological data"
    )
    
    parser.add_argument(
        "--shuffle-options",
        action="store_true",
        help="Randomly shuffle options within each question"
    )
    
    parser.add_argument(
        "--sample", "-s",
        type=int,
        metavar="N",
        help="Evaluate only N sample questions"
    )

    parser.add_argument(
        "--year", "-y",
        type=int,
        help="Evaluate only questions from a specific benchmark year (e.g., 2022)"
    )
    
    parser.add_argument(
        "--categories", "-c",
        nargs="+",
        choices=["事业", "健康", "外貌", "婚姻", "子女", "学业", "官非", "家庭", "性格", "灾劫", "财运", "运势"],
        help="Filter questions by categories"
    )
    
    # Data options
    parser.add_argument(
        "--data-path",
        help="Path to benchmark data file"
    )

    parser.add_argument(
        "--fortune-data-path",
        help="Path to fortune_api_results.json for chart utilities"
    )
    
    # Output options
    parser.add_argument(
        "--output-dir", "-o",
        default="logs",
        help="Directory to save results (default: logs)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to files"
    )
    
    # Performance options
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum concurrent API calls (default: 5)"
    )
    
    # Configuration
    parser.add_argument(
        "--env-file",
        help="Path to .env file"
    )

    parser.add_argument(
        "--platform",
        choices=["openai", "openrouter", "anthropic", "google", "deepseek", "doubao"],
        help="Force routing platform (overrides auto-detection from model name prefix)",
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List supported models and exit"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show dataset statistics and exit"
    )

    parser.add_argument(
        "--hour-branch",
        type=int,
        metavar="HOUR",
        help="Print the earthly branch for a 24-hour clock hour and exit"
    )

    parser.add_argument(
        "--analyze-pillars",
        metavar="PILLARS",
        help='Parse four Bazi pillars such as "甲寅 戊辰 己亥 壬申" and exit'
    )

    parser.add_argument(
        "--bazi-date",
        metavar="YYYY-MM-DD",
        help="Calculate Bazi pillars from a Gregorian date and exit"
    )

    parser.add_argument(
        "--bazi-time",
        metavar="HH:MM",
        help="Optional 24-hour time used with --bazi-date, for example 16:40"
    )

    parser.add_argument(
        "--bazi-location",
        help="Optional birth location used with --bazi-date, for example 台湾 or malaysia"
    )

    parser.add_argument(
        "--bazi-country",
        help="Optional birth country used with --bazi-date when location is broad"
    )

    parser.add_argument(
        "--bazi-case",
        metavar="CASE_ID",
        help="Calculate Bazi from a benchmark case birth_info and compare fixture pillars"
    )

    parser.add_argument(
        "--show-chart",
        metavar="CASE_ID",
        help="Print a normalized Bazi/Ziwei chart summary for a benchmark case_id and exit"
    )
    
    args = parser.parse_args()
    
    # Handle special actions
    if args.list_models:
        print("Supported models by provider:")
        for provider, models in ModelFactory.list_supported_models().items():
            print(f"\n{provider.capitalize()}:")
            for model in models:
                print(f"  - {model}")
        return 0
    
    if args.stats:
        try:
            loader = DataLoader(args.data_path)
            stats = loader.get_statistics(year=args.year)
        except Exception as e:
            logger.error(f"Failed to load dataset statistics: {e}")
            return 1
        print(f"\nDataset Statistics:")
        print(f"  Name: {stats['benchmark_name']}")
        print(f"  Version: {stats['data_version']}")
        print(f"  Available Years: {', '.join(map(str, stats['available_years']))}")
        if args.year is not None:
            print(f"  Selected Year: {args.year}")
        print(f"  Total Questions: {stats['total_questions']}")
        print(f"\n  Categories:")
        for cat, count in stats['categories'].items():
            print(f"    - {cat}: {count}")
        return 0

    if args.hour_branch is not None:
        try:
            print(hour_branch(args.hour_branch))
            return 0
        except Exception as e:
            logger.error(f"Failed to calculate hour branch: {e}")
            return 1

    if args.analyze_pillars:
        try:
            print(json.dumps(parse_bazi_pillars(args.analyze_pillars), ensure_ascii=False, indent=2))
            return 0
        except Exception as e:
            logger.error(f"Failed to analyze Bazi pillars: {e}")
            return 1

    if args.bazi_date:
        try:
            hour = None
            minute = 0
            if args.bazi_time:
                time_parts = args.bazi_time.split(":", 1)
                if len(time_parts) != 2:
                    raise ValueError("--bazi-time must use HH:MM format")
                hour = int(time_parts[0])
                minute = int(time_parts[1])
            timezone = (
                resolve_timezone(args.bazi_location, country=args.bazi_country)
                if args.bazi_location or args.bazi_country
                else None
            )
            chart = bazi_from_gregorian(
                args.bazi_date,
                hour=hour,
                minute=minute,
                tz_offset_hours=timezone.utc_offset_hours if timezone else 8.0,
            )
            if timezone:
                chart["timezone"] = timezone.as_dict()
                chart["warnings"] = list(chart["warnings"]) + list(timezone.warnings)
            print(json.dumps(
                chart,
                ensure_ascii=False,
                indent=2,
            ))
            return 0
        except Exception as e:
            logger.error(f"Failed to calculate Bazi pillars: {e}")
            return 1

    if args.bazi_case:
        try:
            record = get_chart_record(args.bazi_case, path=args.fortune_data_path)
            computed = bazi_from_birth_info(record.get("birth_info") or {})
            fixture = extract_bazi_summary(record)
            computed_pillars = " ".join(
                [
                    computed["year_pillar"],
                    computed["month_pillar"],
                    computed["day_pillar"],
                    computed["hour_pillar"] or "",
                ]
            ).strip()
            fixture_pillars = fixture["chinese_date"]
            print(json.dumps(
                {
                    "case_id": args.bazi_case,
                    "computed_bazi": computed,
                    "fixture_bazi": fixture,
                    "computed_pillars": computed_pillars,
                    "fixture_pillars": fixture_pillars,
                    "matches_fixture": computed_pillars == fixture_pillars,
                },
                ensure_ascii=False,
                indent=2,
            ))
            return 0
        except Exception as e:
            logger.error(f"Failed to calculate Bazi for case: {e}")
            return 1

    if args.show_chart:
        try:
            print(json.dumps(
                get_chart_summary(args.show_chart, path=args.fortune_data_path),
                ensure_ascii=False,
                indent=2,
            ))
            return 0
        except Exception as e:
            logger.error(f"Failed to show chart: {e}")
            return 1
    
    # Check if model is required for remaining operations
    if not args.model:
        parser.error("--model is required unless using --list-models or --stats")
    
    # Load configuration
    try:
        from .utils.config import load_config

        config = load_config(args.env_file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1
    
    # Create model client
    try:
        logger.info(f"Creating model client for {args.model}")
        model_client = ModelFactory.create(args.model, provider=args.platform, config=config)
    except Exception as e:
        logger.error(f"Failed to create model client: {e}")
        return 1
    
    # Validate API key
    if not model_client.validate_api_key():
        logger.error("Invalid API key. Please check your configuration.")
        return 1
    
    # Create benchmark
    from .benchmark import FortuneTellingBenchmark

    benchmark = FortuneTellingBenchmark(model_client, args.data_path)
    
    # Run evaluation
    try:
        logger.info("Starting benchmark evaluation...")
        results = benchmark.evaluate(
            use_cot=args.cot,
            use_astro=args.astro,
            sample_size=args.sample,
            year=args.year,
            categories=args.categories,
            shuffle_options=getattr(args, 'shuffle_options', False),
            max_workers=args.max_workers
        )
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"Evaluation Results - {args.model}")
        print(f"{'='*50}")
        if args.year is not None:
            print(f"Benchmark Year: {args.year}")
        print(f"Overall Accuracy: {results['overall_accuracy']:.2%}")
        print(f"Total Questions: {results['total_questions']}")
        print(f"Correct Answers: {results['correct_answers']}")
        
        if results['errors'] > 0:
            print(f"Errors: {results['errors']}")
        
        print(f"\nCategory Breakdown:")
        for cat, stats in results['category_stats'].items():
            print(f"  {cat:12s}: {stats['accuracy']:6.2%} ({stats['correct']}/{stats['total']})")
        
        print(f"\nEvaluation Time: {results['evaluation_time']:.2f}s")
        print(f"Avg Response Time: {results['average_response_time']:.2f}s")
        
        # Save results
        if not args.no_save:
            benchmark.save_results(results, args.output_dir)
            print(f"\nResults saved to {args.output_dir}/")
        
    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
