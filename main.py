#################### 함수 목록 ####################

# 함수 : 지도 생성 -> 리스트 - 지도, 지도 좌표
def create_map(col: int, location: list) -> list:
    schoolMap = []
    rMap = []
    for idx, loc in enumerate(location):
        rMap.append(loc)
        if (idx + 1) % col == 0:
            schoolMap.append(rMap)
            rMap = []
    return schoolMap

# 함수 : 이동 -> 입력이 유효한지 판단 후 이동 출력
def move_char(loc_str: str):
    print()
    direction_block = "그 방향은 막혔어"
    if loc_str == "w":
        if check_move(location_idx, 0, 1):
            location_idx[0] += 1
            print(f"현재 위치: {schoolMap[location_idx[0]][location_idx[1]]}")
        else:
            print(direction_block)

    elif loc_str == "s":
        if check_move(location_idx, 0, -1):
            location_idx[0] -= 1
            print(f"현재 위치: {schoolMap[location_idx[0]][location_idx[1]]}")
        else:
            print(direction_block)

    elif loc_str == "a":
        if check_move(location_idx, 1, -1):
            location_idx[1] -= 1
            print(f"현재 위치: {schoolMap[location_idx[0]][location_idx[1]]}")
        else:
            print(direction_block)

    elif loc_str == "d":
        if check_move(location_idx, 1, 1):
            location_idx[1] += 1
            print(f"현재 위치: {schoolMap[location_idx[0]][location_idx[1]]}")
        else:
            print(direction_block)
    else:
        print("잘못된 입력입니다.")

# 함수 : 이동 유효성 검사 -> 불리언 - 이동 가능 여부
def check_move(loc_idx: list, idx: int, num: int) -> bool:
    afterMove = loc_idx.copy()
    afterMove[idx] = afterMove[idx] + num
    validity = True

    try:
        schoolMap[afterMove[0]][afterMove[1]]
        if (afterMove[idx] < 0) or (schoolMap[afterMove[0]][afterMove[1]] == 0):
            validity = False
    except IndexError:
        validity = False

    return validity


#################### 변수 목록 ####################

# 변수 : 주인공 상태 -> 딕셔너리 - 배고픔정도
char_stat = {
    "levelHunger": "배고픔",
    }

# 변수 : 환경 상태 -> 딕셔너리 - 시간
env_stat = {
    "time": 1100
    }

# 변수 : 위치 -> 리스트 - [x,y]
location = "연대앞 버스정류장"
location_idx = [0, 0]

# 학교 위치
school_locations = [
    "연대앞 버스정류장",
    "정문",
    "세브란스병원 버스정류장",
    "공학원",
    "백양로1",
    "공터1",
    "공학관",
    "백양로2",
    "백주년기념관",
]

# 학교 지도 및 좌표
schoolMap = create_map(3, school_locations)

if __name__ == "__main__":
    gameplay = True
    while gameplay:
        user_input = input("\n이동할 방향을 입력하세요 (w/s/a/d): ")
        move_char(user_input)