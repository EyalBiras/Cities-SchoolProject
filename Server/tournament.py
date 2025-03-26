import json
import pathlib
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BANNED_WORDS = ["TimeoutError", "Engine", "internal_update_flag", "BaseException", "_City__people_amount",
                "_City__level", "_City__action", "_City__position", "_City__id", '_Group__people_amount',
                '_Group__source', '_Group__destination', '_Group__turns_till_arrival', "_Group__position",
                "_Group__speed", "_Group__velocity", "_Group__animation_phase", "_Game__player", "_Game__enemy",
                "_Game__neutral", "_Game__turn", "_Game__logger", "_Player__cities", "_Player__capital_city",
                "_Player__groups", "_Player__conquered_cities", "_Player__lost_cities"]
BANNED_FUNCTIONS = ["open", "input", "eval", "exec", "compile", "memoryview", "exit", "__import__"]
ALLOWED_MODULES = ["cities_game", "abc", "collections", "itertools", "numpy", "enum", "math", "dataclasses",
                   "functools"]
NEEDED_WORDS_FOR_MAIN = ["class MyBot(Bot):"]
FILE = Path(__file__)
GROUPS = FILE.parent / "groups"
GAMES_BASE_PATH = FILE.parent
TOURNAMENT_CODE_DIR = "tournament_code"
RESULTS_FILE = FILE.parent / "results.json"
EXCEPT_EXCEPTION_PATTERN = r"^\s*except\s+Exception\s*(?:as\s+\w+)?\s*:\s*$"


def get_all_import_modules(text: str) -> list[str]:
    pattern = r"(from\s+(\S+)\s+import|import\s+(\S+))"
    modules = [match[1] if match[1] else match[2] for match in re.findall(pattern, text)]
    return modules


def validate_imports(modules: list[str], group_files: list[str]) -> bool:
    allowed_modules = ALLOWED_MODULES + group_files
    for module in modules:
        if module not in allowed_modules and not module.startswith("numpy"):
            return False
    return True


def is_function_appear(contents: str, function_name: str) -> bool:
    pattern = fr"\b{function_name}\b"
    return bool(re.search(pattern, contents))


def validate_main(contents: str) -> bool:
    for word in NEEDED_WORDS_FOR_MAIN:
        if word not in contents:
            return False
    return True


def validate_functions(contents: str) -> bool:
    for function in BANNED_FUNCTIONS:
        if is_function_appear(contents, function_name=function):
            return False
    return True


def validate_bad_words(contents: str) -> bool:
    for word in BANNED_WORDS:
        if word in contents:
            return False
    return True


def is_python(file: Path) -> bool:
    if not file.is_file():
        return False
    return file.name.endswith(".py")


def reset_results(groups: list[str]) -> None:
    with open(RESULTS_FILE, "w") as f:
        results = {group: {"total score": 0, "wins": 0, "losses": 0, "draws": 0} for group in groups}
        json.dump(results, f, indent=2)


def validate_file(file: Path, group_files: list[str]) -> bool:
    with open(file) as f:
        contents = f.read()

    if not validate_imports(get_all_import_modules(contents), group_files):
        return False

    if file.name == "main.py":
        with open(file, "r") as f:
            contents = f.read()
            if not validate_main(contents):
                return False

    with open(file, "r") as f:
        contents = f.read()
        if not validate_bad_words(contents):
            return False
        if not validate_functions(contents):
            return False
        lines = contents.splitlines()
        for line in lines:
            if re.match(EXCEPT_EXCEPTION_PATTERN, line):
                return False
    return True


def validate_group(group: Path) -> bool:
    files = [Path(file) for file in group.rglob("*") if is_python(file)]
    group_files = [file.name.replace(".py", "") for file in files]
    found_main = False
    for file in files:
        if file.name == "main.py":
            found_main = True
        if not validate_file(file, group_files):
            return False
    return found_main


def battle(group: Path, enemy: Path, games_directory: Path) -> None:
    if not validate_group(group / "development_code") or not validate_group(enemy / TOURNAMENT_CODE_DIR):
        return
    game_path = GAMES_BASE_PATH / f"{group.name}-{enemy.name}.py"
    with open(game_path, "w") as f:
        f.write("from cities_game.engine import Engine\n")
        f.write("from utils import reset_game\n")
        f.write("from utils import images_to_video\n")
        f.write(f"import groups.{group.name}.{'development_code'}.main as {group.name}\n")
        f.write(f"import groups.{enemy.name}.{'tournament_code'}.main as {enemy.name}\n")
        f.write(f"from pathlib import Path\n")
        f.write(f"import json\n")
        f.write(f"import gzip\n")
        f.write(f"import time\n")
        f.write(f"\n")
        f.write(f"RESULTS_FILE = Path(r'{RESULTS_FILE}')\n")
        f.write(f"\n")
        f.write(f"if __name__ == '__main__':\n")
        f.write(f"\tp1, p2, neutral_player, decorations = reset_game()\n")
        f.write(
            f"\te = Engine(p1,{group.name}.MyBot(),'{group.name}', p2,{enemy.name}.MyBot(), '{enemy.name}', neutral_player, decorations,game_name='{group.name} vs {enemy.name}', is_tournament=False)\n")
        f.write(f"\tgame, winner = e.make_game()\n")
        f.write(f"\n")
        f.write(
            f"\tgame_file = r'{games_directory}\\{enemy.name}\\{group.name} vs {enemy.name}-winner-' + winner + '.json.gzip'\n")
        f.write(
            f"\twith gzip.open(game_file, 'wt', encoding='utf-8') as f:\n")
        f.write(f"\t\tjson.dump(game, f)\n")
    print(game_path)
    # with open(game_path, "r") as f:
    #     exec(f.read(), {"__name__": "__main__"})

    subprocess.run([sys.executable, game_path])
    game_path.unlink()


def run_game(group1: Path, group2: Path, games_directory: str = GAMES_BASE_PATH / "games",
             code_directory: str = TOURNAMENT_CODE_DIR):
    game_path = GAMES_BASE_PATH / f"{group1.name}-{group2.name}.py"
    t = time.perf_counter()
    with open(game_path, "w") as f:
        f.write("from cities_game.engine import Engine\n")
        f.write("from utils import reset_game\n")
        f.write("from utils import images_to_video\n")
        f.write(f"import groups.{group1.name}.{code_directory}.main as {group1.name}\n")
        f.write(f"import groups.{group2.name}.{code_directory}.main as {group2.name}\n")
        f.write(f"from pathlib import Path\n")
        f.write(f"import json\n")
        f.write(f"import gzip\n")
        f.write(f"import time\n")
        f.write(f"\n")
        f.write(f"RESULTS_FILE = Path(r'{RESULTS_FILE}')\n")
        f.write(f"\n")
        f.write(f"if __name__ == '__main__':\n")
        f.write(f"\tp1, p2, neutral_player, decorations = reset_game()\n")
        f.write(
            f"\te = Engine(p1,{group1.name}.MyBot(),'{group1.name}', p2,{group2.name}.MyBot(), '{group2.name}', neutral_player, decorations)\n")
        f.write(f"\tgame, winner = e.make_game()\n")
        f.write(
            f"\twith gzip.open(r'{games_directory}\\{group1.name} vs {group2.name}-winner-' + winner +'.json.gzip', 'wt', encoding='utf-8') as f:\n")
        f.write(f"\t\tjson.dump(game, f)\n")
        f.write(f"\twith open(RESULTS_FILE) as f:\n")
        f.write(f"\t\tresults = json.load(f)\n")
        f.write(f"\n")
        f.write(f"\tif winner == '{group1.name}':\n")
        f.write(f"\t\tresults['{group1.name}']['wins'] += 1\n")
        f.write(f"\t\tresults['{group2.name}']['losses'] += 1\n")
        f.write(f"\telif winner == '{group2.name}':\n")
        f.write(f"\t\tresults['{group2.name}']['wins'] += 1\n")
        f.write(f"\t\tresults['{group1.name}']['losses'] += 1\n")
        f.write(f"\telse:\n")
        f.write(f"\t\tresults['{group2.name}']['draws'] += 1\n")
        f.write(f"\t\tresults['{group1.name}']['draws'] += 1\n")
        f.write(f"\n")
        f.write(f"\twith open(RESULTS_FILE, 'w') as f:\n")
        f.write(f"\t\tjson.dump(results, f, indent=2)\n")
        f.write(f"\n")
    # with open(game_path, "r") as f:
    #     exec(f.read(), {"__name__": "__main__"})
    subprocess.run([sys.executable, game_path])
    print(time.perf_counter() - t)
    game_path.unlink()


def move_development_to_tournament(group: str) -> None:
    shutil.copytree(GROUPS / f"{group}" / "development_code", GROUPS / f"{group}" / TOURNAMENT_CODE_DIR,
                    dirs_exist_ok=True)


def run_tournament():
    games_path = GAMES_BASE_PATH / "games"
    if games_path.exists() and games_path.is_dir():
        for item in games_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    games_path.mkdir(parents=True, exist_ok=True)

    t1 = time.perf_counter()
    groups = [Path(file).name for file in GROUPS.glob("*") if validate_group(Path(file / "development_code"))]
    for group in groups:
        move_development_to_tournament(group)
    reset_results(groups)
    for i, group in enumerate(groups):
        for group2 in groups[i + 1:]:
            print(f"{group} vs {group2}")
            run_game(Path(f"groups/{group}"), Path(f"groups/{group2}"))

    with open(RESULTS_FILE) as f:
        results = json.load(f)

    for group in groups:
        results[group]["total score"] = results[group]["wins"] + 0.5 * results[group]["draws"]
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(list(GROUPS.glob("*")))
    print(time.perf_counter() - t1)

run_tournament()