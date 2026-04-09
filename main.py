import os
import datetime

# ------------------ 함수 목록 ------------------#

# 지도 생성 : 리스트 - 지도, 지도 좌표
def create_map(col: int, location: list) -> list:
    schoolMap = []
    rMap = []
    for idx, loc in enumerate(location):
        rMap.append(loc)
        if (idx + 1) % col == 0:
            schoolMap.append(rMap)
            rMap = []
    return schoolMap


# 이동 : 입력이 유효한지 판단 후 이동 출력
def move_char(loc_str: str):
    print("\n" + SEP_1)
    directions = {
        "w": (0, 1),
        "s": (0, -1),
        "a": (1, -1),
        "d": (1, 1),
    }

    if loc_str not in directions:
        print("  잘못된 입력입니다.")
        return 

    idx, num = directions[loc_str]

    if check_move(location_idx, idx, num):
        char_stat["hp"] -= 1
        global location
        location_idx[idx] += num
        location = schoolMap[location_idx[0]][location_idx[1]]
        print(f"  현재 위치: {location}")w
        do_interaction(location)
    else:
        print("  막힌 방향입니다.")

    print(SEP_1)
    

# 이동 유효성 검사 : 불리언 - 이동 가능 여부
def check_move(loc_idx: list, idx: int, num: int) -> bool:
    afterMove = loc_idx.copy()
    afterMove[idx] = afterMove[idx] + num
    validity = True

    try:
        schoolMap[afterMove[0]][afterMove[1]]
        if (afterMove[idx] < 0) or (schoolMap[afterMove[0]][afterMove[1]] == None):
            validity = False
    except IndexError:
        validity = False

    return validity


# 상태 출력
def print_status():
    print("\n" + SEP_1)
    print("[ 상태 ]")
    print(f"  체력:   {char_stat['hp']}")
    print(f"  소지금: {char_stat['money']}원")
    print(SEP_1)


# 가방 열기 : 아이템 이름 및 특성 출력
def open_bag():
    while True:
        print("\n" + SEP_1)
        print("[ 가방 ]")
        if not char_stat["bag"]:
            print("  가방이 비어있습니다.")
            print(SEP_1)
            break
        for i, (name, count) in enumerate(char_stat["bag"].items(), 1):
            hp_recover = item_dict[name][1]
            print(f"  {i}. {name}  x{count}  (HP +{hp_recover})")
        print(SEP_1)
        user_input = input("사용할 아이템 번호 입력 (q: 닫기): ")
        if user_input == "q":
            break
        use_item(user_input)


# 아이템 사용 : idx 기반 및 이름 기반 처리
def use_item(user_input: str):
    items = list(char_stat["bag"].items())

    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(items):
            name = items[idx][0]
        else:
            print("  없는 번호입니다.")
            return
    elif user_input in char_stat["bag"]:
        name = user_input
    else:
        print("  가방에 없는 아이템입니다.")
        return

    recover = item_dict[name][1]
    char_stat["hp"] += recover
    char_stat["bag"][name] -= 1
    print(f"\n  → {name} 사용 (HP +{recover}, 현재 HP: {char_stat['hp']})")
    clean_inventory()


# 가방 정리 : 0개인 아이템 제거
def clean_inventory():
    char_stat["bag"] = {k: v for k, v in char_stat["bag"].items() if v != 0}


# 상호작용 : 지점 도착 시 상호작용 실행
def do_interaction(location: str):
    if location in interaction:
        print(SEP_1)
        print(f"\n  ★ {location}에 상점이 있습니다.")
        a = input("  상점에 들어가시겠습니까? [y/n]: ")
        print()
        if a == "y":
            buy_item(location)


# 상호작용 : 아이템 구매하기 - idx 및 이름 기반 처리
def buy_item(location: str):
    while True:
        shop = interaction[location]
        items = list(shop.items())
        print("\n" + SEP_1)
        print(f"[ {location} 상점 ] - 소지금 {char_stat['money']}원\n")
        for i, (name, stock) in enumerate(items, 1):
            price = item_dict[name][0]
            print(f"  {i}. {name}  {price}원  (재고: {stock})")
        print(SEP_1)
        buy_input = input("구매할 아이템 번호 입력 (q: 닫기): ")

        if buy_input == "q":
            break

        name = None
        if buy_input.isdigit():
            idx = int(buy_input) - 1
            if 0 <= idx < len(items):
                name = items[idx][0]
            else:
                print("  없는 번호입니다.")
                continue
        elif buy_input in shop:
            name = buy_input
        else:
            print("  없는 아이템입니다.")
            continue

        price = item_dict[name][0]
        if shop[name] <= 0:
            print("  재고가 없습니다.")
        elif char_stat["money"] >= price:
            char_stat["money"] -= price
            shop[name] -= 1
            if name in char_stat["bag"]:
                char_stat["bag"][name] += 1
            else:
                char_stat["bag"][name] = 1
            print(f"\n  → {name} 구매 완료 (잔액: {char_stat['money']}원)")
        else:
            print(f"\n  돈이 부족합니다. (필요: {price}원, 보유: {char_stat['money']}원)")


# 난이도 설정 : idx 및 이름 기반 처리 - 시작 및 게임 도중 호출
def set_difficulty():
    difficulty = ["쉬움", "보통", "어려움"]
    prepGame = True
    while prepGame:
        prepGame = False
        print("\n" + SEP_1)
        diff = input("난이도를 설정하시오 - [1. 쉬움, 2. 보통, 3. 어려움]: ")
        print(SEP_1)
        if diff == "1" or diff == "쉬움":
            settings["difficulty"] = difficulty[0]
        elif diff == "2" or diff == "보통":
            settings["difficulty"] = difficulty[1]
        elif diff == "3" or diff == "어려움":
            settings["difficulty"] = difficulty[2]
        else:
            print("\n  잘못된 입력입니다\n")
            print(SEP_1)
            prepGame = True
    print(f"  난이도가 {settings['difficulty']}으로 설정되었습니다.")
    print(SEP_1)


# 게임 저장하기 : 폴더 생성 후 각 요소 추가하기
def save_game():
    print("\n" + SEP_1)
    file_name = input("저장할 파일 이름을 입력하세요: ")
    os.makedirs('saves', exist_ok=True)
    with open(f"saves/{file_name}.txt", "w") as f:
        f.write(f"char_stat: {char_stat}\n")
        f.write(f"location: {location}\n")
        f.write(f"location_idx: {location_idx}\n")
        f.write(f"difficulty: {settings['difficulty']}\n")
    print(f"  {file_name}으로 저장되었습니다.")
    print(SEP_1)


# 게임 불러오기 : 폴더에서 파일 선택 후 각 요소 불러오기 - 폴더 변경 가능
def load_game():
    global char_stat, location, location_idx, env_stat
    print("\n" + SEP_1)
    load_list = ["char_stat", "location", "location_idx", "difficulty"]
    save_dir = "saves"
    file_list = os.listdir(save_dir)
    for i, file in enumerate(file_list):
        print(f"{i+1}. {file}")

    file_name = input("불러올 파일 번호를 입력하세요 (0: 폴더 변경): ")

    if file_name == "0":
        save_dir = input("불러올 폴더 경로를 입력하세요: ").strip()

        if not os.path.isdir(save_dir):
            print("  존재하지 않는 폴더입니다.")
            print(SEP_1)
            return
        file_list = os.listdir(save_dir)

        for i, file in enumerate(file_list):
            print(f"{i+1}. {file}")

        file_name = input("불러올 파일 번호를 입력하세요: ")

        if file_name.isdigit() and 1 <= int(file_name) <= len(file_list):
            file_name = file_list[int(file_name)-1]
        else:
            print("  잘못된 입력입니다.")
            print(SEP_1)
            return

    elif file_name.isdigit() and 1 <= int(file_name) <= len(file_list):
        file_name = file_list[int(file_name)-1]

    else:
        print("  잘못된 입력입니다.")
        print(SEP_1)
        return

    with open(os.path.join(save_dir, file_name), "r") as save_file:
        for line in save_file:
            line = line.strip()
            if line.startswith(load_list[0] + ": "):
                char_stat = eval(line[len(load_list[0]) + 2:])
            elif line.startswith(load_list[1] + ": "):
                location = line[len(load_list[1]) + 2:]
            elif line.startswith(load_list[2] + ": "):
                location_idx = eval(line[len(load_list[2]) + 2:])
            elif line.startswith(load_list[3] + ": "):
                settings["difficulty"] = line[len(load_list[3]) + 2:]
    print(f"  {file_name}을 불러왔습니다.")
    print(SEP_1)

# ------------------ 변수 목록 ------------------#

# 출력 구분선
SEP_1 = "-" * 60
SEP_2 = "=" * 60

# 주인공 상태 -> 딕셔너리
char_stat = {
    "hp": 10, 
    "stamina": "배고픔", 
    "money": 50000, 
    "bag": {}
}

# 아이템 -> 딕셔너리 - [가격, 회복량]
item_dict = {
    "두쫀쿠": [2500, 25], 
    "카페라떼": [5000, 25]
}

# 상호작용 -> 딕셔너리 - [가격, 재고]
interaction = {
    "학생회관": {"두쫀쿠": 50, "카페라떼": 100}
}

# 위치 -> 리스트 - [x, y]
location = "연대앞 버스정류장"
location_idx = [0, 0]

# 학교 위치 -> 연대앞 버스정류장 ~ 이윤재관
school_locations = [
    "연대앞 버스정류장", "정문", "스타벅스", "세브란스병원 버스정류장", None, None,
    "공학원", "백양로1", "공터1", "암병원", "의과대학", None,
    "공학관", "백양로2", "백주년기념관", "안과병원", "제중관", None,
    "체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스병원",
    "중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학",
    "백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC",
    None, None, None, None, "새천년관", "이윤재관",
]

# 함수 생성 -> 학교 지도 및 좌표 - n개의 열을 가지는 지도 생성
schoolMap = create_map(6, school_locations)

# 설정 -> 딕셔너리 - 난이도
settings = {
    "difficulty": "보통"
}


# ------------------ 메인 함수 ------------------#
if __name__ == "__main__":
    set_difficulty()
    print("\n" + SEP_2)
    print(f"  당신은 지금 {location}에 있습니다.")
    print(SEP_2)
    

    while True:
        print("\n  조작: 이동(w/a/s/d) | 가방(b) | 상태(v) | 설정(o) | 저장(1) | 불러오기(2) | 종료(q)")
        user_input = input("\n입력: ")

        if user_input == "q":
            print("\n" + SEP_1)
            print("게임을 종료합니다")
            print(SEP_1)
            break
        
        elif user_input == "v":
            print_status()

        elif user_input == "b":
            open_bag()
        
        elif user_input == "o":
            set_difficulty()

        elif user_input == "1":
            save_game()

        elif user_input == "2":
            load_game()

        else:
            move_char(user_input)
