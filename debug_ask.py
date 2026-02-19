import argparse
import sys

from sophie_janitor import SophieJanitor


def main():
    parser = argparse.ArgumentParser(
        description="Debug CLI for SophieJanitor.ask()"
    )
    parser.add_argument(
        "question",
        type=str,
        help="Question à poser au système"
    )

    args = parser.parse_args()

    print("Initialisation de SophieJanitor...")
    sj = SophieJanitor()

    print("Question :", args.question)
    print("Appel de ask()...\n")

    try:
        response = sj.ask(args.question)

        print("=== RÉPONSE ===")
        print(response)

    except Exception as e:
        print("Erreur pendant l'exécution :")
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
