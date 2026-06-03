"""
Command-line interface for Fortune Telling Benchmark.
"""

import argparse
import json
import sys

from .agent import MingLiAgent
from .agent_eval import (
    AgentEvalConfig,
    SUPPORTED_EVENT_TYPE_GUARDS,
    append_agent_eval_record,
    evaluate_agent_questions,
    format_agent_eval_summary,
    load_agent_eval_questions,
    start_agent_eval_run,
    summarize_agent_eval,
    write_agent_eval_summary,
)
from .agent_eval_report import (
    build_agent_eval_analysis,
    compare_agent_eval_runs,
    format_agent_eval_comparison,
    format_agent_eval_analysis,
    load_agent_eval_run,
)
from .api import run_server
from .calendar import hour_branch, parse_bazi_pillars
from .candidate_years import SCORING_VARIANTS
from .chart_api import build_bazi_chart
from .charts import extract_bazi_summary, get_chart_record, get_chart_summary
from .bazi import bazi_from_birth_info, bazi_from_gregorian
from .locations import resolve_timezone
from .lunar import lunar_from_solar_date, parse_chinese_lunar_date, solar_from_lunar_date
from .interactive import collect_agent_input, format_agent_result, prompt_for_model_choice
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
  python -m mingli_bench.cli --lunar-date "一九八四年闰十月十七"
  python -m mingli_bench.cli --lunar-from-solar 1978-04-05
  python -m mingli_bench.cli --solar-from-lunar "一九七八年二月廿八"
  python -m mingli_bench.cli --chart-input-json '{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾"}'
  python -m mingli_bench.cli --agent-input-json '{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾"}' --agent-question "分析事业和性格"
  python -m mingli_bench.cli --agent-input-json '{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾"}' --agent-model google/gemini-2.5-pro
  python -m mingli_bench.cli agent --no-llm
  python -m mingli_bench.cli agent --no-llm --show-prompt
  mingli-bench agent --model google/gemini-2.5-pro
  mingli-bench eval-agent --sample 10
  mingli-bench eval-agent --model google/gemini-2.5-pro --sample 10
  mingli-bench serve --port 8765
  mingli-bench serve --model google/gemini-2.5-pro
  python -m mingli_bench.cli --show-chart case_1
        """
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=[
            "agent",
            "serve",
            "eval-agent",
            "analyze-agent-eval",
            "compare-agent-evals",
        ],
        help=(
            "Optional command. Use 'agent' for the interactive CLI, "
            "'serve' for the local HTTP API, 'eval-agent' for agent pipeline "
            "evaluation, 'analyze-agent-eval' for saved eval reports, "
            "or 'compare-agent-evals' for A/B run comparisons."
        )
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
        "--run-dir",
        help="For 'analyze-agent-eval': directory containing summary.json and records.jsonl."
    )

    parser.add_argument(
        "--base-run-dir",
        help="For 'compare-agent-evals': baseline run directory.",
    )

    parser.add_argument(
        "--candidate-run-dir",
        help="For 'compare-agent-evals': candidate run directory.",
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
        "--lunar-date",
        metavar="LUNAR_DATE",
        help='Parse a Chinese lunar date such as "一九八四年闰十月十七" and exit'
    )

    parser.add_argument(
        "--lunar-from-solar",
        metavar="YYYY-MM-DD",
        help="Look up fixture-backed lunar date for a Gregorian date and exit"
    )

    parser.add_argument(
        "--solar-from-lunar",
        metavar="LUNAR_DATE",
        help="Look up fixture-backed Gregorian date for a Chinese lunar date and exit"
    )

    parser.add_argument(
        "--chart-input-json",
        metavar="JSON",
        help="Build a stable BaziChart from a ChartInput JSON object and exit"
    )

    parser.add_argument(
        "--agent-input-json",
        metavar="JSON",
        help="Run the local MingLi agent from a ChartInput JSON object and exit"
    )

    parser.add_argument(
        "--agent-question",
        default="请基于这个八字命盘，给出结构化、审慎的中文命理分析。",
        help="Question or task for --agent-input-json"
    )

    parser.add_argument(
        "--agent-model",
        help="Optional model name for --agent-input-json. If omitted, returns chart and prompt only."
    )

    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="For 'agent': do not ask for or call an LLM"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="For 'agent': output JSON instead of a readable terminal summary"
    )

    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="For 'agent': include the generated LLM prompt in readable output"
    )

    parser.add_argument(
        "--include-candidate-year-diagnostics",
        action="store_true",
        help=(
            "Experimental: include activation-weighted candidate-year "
            "diagnostics in agent prompts."
        ),
    )

    parser.add_argument(
        "--candidate-year-override-variant",
        choices=sorted(SCORING_VARIANTS),
        help=(
            "Experimental: for eval-agent, override candidate-year answers "
            "with the top local scoring variant while preserving the model "
            "choice in model_predicted_answer."
        ),
    )

    parser.add_argument(
        "--event-type-guard",
        choices=sorted(SUPPORTED_EVENT_TYPE_GUARDS),
        help=(
            "Experimental: for eval-agent, apply a narrow event-type "
            "post-processor while preserving the model choice in "
            "model_predicted_answer."
        ),
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="For 'serve': API host address (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="For 'serve': API port (default: 8765)"
    )

    parser.add_argument(
        "--api-model",
        help="For 'serve': optional model name for /agent. Defaults to --model when provided."
    )

    parser.add_argument(
        "--show-chart",
        metavar="CASE_ID",
        help="Print a normalized Bazi/Ziwei chart summary for a benchmark case_id and exit"
    )
    
    args = parser.parse_args()

    if args.command == "agent":
        try:
            model_prompt_input = input
            if args.json:
                def input_on_stderr(prompt_text: str) -> str:
                    sys.stderr.write(prompt_text)
                    sys.stderr.flush()
                    return sys.stdin.readline()

                model_prompt_input = input_on_stderr
                output_func = lambda line: print(line, file=sys.stderr)
                payload, question = collect_agent_input(
                    input_func=input_on_stderr,
                    output_func=output_func,
                )
            else:
                payload, question = collect_agent_input()
            model_name = None
            if not args.no_llm:
                model_name = args.agent_model or args.model or prompt_for_model_choice(
                    input_func=model_prompt_input,
                )
            model_client = None
            if model_name:
                from .utils.config import load_config

                config = load_config(args.env_file)
                model_client = ModelFactory.create(
                    model_name,
                    provider=args.platform,
                    config=config,
                )
            result = MingLiAgent(
                model_client,
                include_candidate_year_diagnostics=(
                    args.include_candidate_year_diagnostics
                ),
            ).run(
                payload,
                question=question,
                fortune_data_path=args.fortune_data_path,
            )
            print(
                format_agent_result(
                    result,
                    as_json=args.json,
                    show_prompt=args.show_prompt,
                )
            )
            return 0
        except Exception as e:
            logger.error(f"Failed to run interactive MingLi agent: {e}")
            return 1

    if args.command == "serve":
        try:
            run_server(
                host=args.host,
                port=args.port,
                fortune_data_path=args.fortune_data_path,
                model_name=args.api_model or args.model,
                provider=args.platform,
                env_file=args.env_file,
            )
            return 0
        except Exception as e:
            logger.error(f"Failed to run MingLi API server: {e}")
            return 1

    if args.command == "eval-agent":
        try:
            model_name = args.agent_model or args.model
            model_client = None
            if model_name:
                from .utils.config import load_config

                config_data = load_config(args.env_file)
                model_client = ModelFactory.create(
                    model_name,
                    provider=args.platform,
                    config=config_data,
                )
            config = AgentEvalConfig(
                sample_size=args.sample,
                year=args.year,
                categories=args.categories,
                data_path=args.data_path,
                fortune_data_path=args.fortune_data_path,
                model_name=model_name,
                output_dir=args.output_dir,
                save=not args.no_save,
                include_candidate_year_diagnostics=(
                    args.include_candidate_year_diagnostics
                ),
                candidate_year_override_variant=(
                    args.candidate_year_override_variant
                ),
                event_type_guard=args.event_type_guard,
            )
            questions = load_agent_eval_questions(config)
            saved_paths = {}
            record_callback = None
            if config.save:
                saved_paths = start_agent_eval_run(args.output_dir)
                print(f"Saving incremental records to: {saved_paths['records']}")

                def record_callback(record):
                    append_agent_eval_record(record, saved_paths["records"])

            records = evaluate_agent_questions(
                questions,
                model_client=model_client,
                fortune_data_path=args.fortune_data_path,
                include_candidate_year_diagnostics=(
                    args.include_candidate_year_diagnostics
                ),
                candidate_year_override_variant=(
                    args.candidate_year_override_variant
                ),
                event_type_guard=args.event_type_guard,
                record_callback=record_callback,
            )
            summary = summarize_agent_eval(records, config=config)
            if config.save:
                write_agent_eval_summary(summary, saved_paths["summary"])
            print(format_agent_eval_summary(summary))
            if saved_paths:
                print("\nSaved:")
                print(f"  Summary: {saved_paths['summary']}")
                print(f"  Records: {saved_paths['records']}")
            return 0
        except Exception as e:
            logger.error(f"Failed to evaluate MingLi agent: {e}")
            return 1

    if args.command == "analyze-agent-eval":
        try:
            if not args.run_dir:
                raise ValueError("--run-dir is required for analyze-agent-eval")
            run = load_agent_eval_run(args.run_dir)
            analysis = build_agent_eval_analysis(
                run["summary"],
                run["records"],
                run_dir=run["run_dir"],
            )
            if args.json:
                print(json.dumps(analysis, ensure_ascii=False, indent=2))
            else:
                print(format_agent_eval_analysis(analysis))
            return 0
        except Exception as e:
            logger.error(f"Failed to analyze MingLi agent eval run: {e}")
            return 1

    if args.command == "compare-agent-evals":
        try:
            if not args.base_run_dir:
                raise ValueError("--base-run-dir is required for compare-agent-evals")
            if not args.candidate_run_dir:
                raise ValueError(
                    "--candidate-run-dir is required for compare-agent-evals"
                )
            comparison = compare_agent_eval_runs(
                load_agent_eval_run(args.base_run_dir),
                load_agent_eval_run(args.candidate_run_dir),
            )
            if args.json:
                print(json.dumps(comparison, ensure_ascii=False, indent=2))
            else:
                print(format_agent_eval_comparison(comparison))
            return 0
        except Exception as e:
            logger.error(f"Failed to compare MingLi agent eval runs: {e}")
            return 1
    
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

    if args.lunar_date:
        try:
            lunar = parse_chinese_lunar_date(args.lunar_date)
            print(json.dumps(lunar.as_dict(), ensure_ascii=False, indent=2))
            return 0
        except Exception as e:
            logger.error(f"Failed to parse lunar date: {e}")
            return 1

    if args.lunar_from_solar:
        try:
            print(json.dumps(
                lunar_from_solar_date(args.lunar_from_solar, path=args.fortune_data_path),
                ensure_ascii=False,
                indent=2,
            ))
            return 0
        except Exception as e:
            logger.error(f"Failed to look up lunar date: {e}")
            return 1

    if args.solar_from_lunar:
        try:
            print(json.dumps(
                solar_from_lunar_date(args.solar_from_lunar, path=args.fortune_data_path),
                ensure_ascii=False,
                indent=2,
            ))
            return 0
        except Exception as e:
            logger.error(f"Failed to look up Gregorian date: {e}")
            return 1

    if args.chart_input_json:
        try:
            payload = json.loads(args.chart_input_json)
            if not isinstance(payload, dict):
                raise ValueError("--chart-input-json must be a JSON object")
            chart = build_bazi_chart(payload, fortune_data_path=args.fortune_data_path)
            print(json.dumps(chart.as_dict(), ensure_ascii=False, indent=2))
            return 0
        except Exception as e:
            logger.error(f"Failed to build Bazi chart: {e}")
            return 1

    if args.agent_input_json:
        try:
            payload = json.loads(args.agent_input_json)
            if not isinstance(payload, dict):
                raise ValueError("--agent-input-json must be a JSON object")
            model_client = None
            if args.agent_model:
                from .utils.config import load_config

                config = load_config(args.env_file)
                model_client = ModelFactory.create(
                    args.agent_model,
                    provider=args.platform,
                    config=config,
                )
            result = MingLiAgent(
                model_client,
                include_candidate_year_diagnostics=(
                    args.include_candidate_year_diagnostics
                ),
            ).run(
                payload,
                question=args.agent_question,
                fortune_data_path=args.fortune_data_path,
            )
            print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
            return 0
        except Exception as e:
            logger.error(f"Failed to run MingLi agent: {e}")
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
