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
    directions = {
        "w": (0, 1),
        "s": (0, -1),
        "a": (1, -1),
        "d": (1, 1),
    }

    if loc_str not in directions:
        print("\n" + "-" * 40)
        print("잘못된 입력입니다.")
        print("-" * 40)
        return

    idx, num = directions[loc_str]

    if check_move(location_idx, idx, num):
        location_idx[idx] += num
        print("\n" + "-" * 40)
        print(f"현재 위치: {schoolMap[location_idx[0]][location_idx[1]]}")
        print("-" * 40)
    else:
        print("\n" + "-" * 40)
        print("그 방향은 막혔어")
        print("-" * 40)


# 함수 : 이동 유효성 검사 -> 불리언 - 이동 가능 여부
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


#################### 변수 목록 ####################

# 변수 : 주인공 상태 -> 딕셔너리 - 배고픔정도
char_stat = {
    "levelHunger": "배고픔",
}

# 변수 : 환경 상태 -> 딕셔너리 - 시간
env_stat = {"time": 1100}

# 변수 : 위치 -> 리스트 - [x,y]
location = "연대앞 버스정류장"
location_idx = [0, 0]

# 변수 : 학교 위치 -> 연대앞 버스정류장 ~ 이윤재관
school_locations = [
    "연대앞버스정류장", "정문", "스타벅스", "세브란스병원버스정류장", None, None,
    "공학원", "백양로1", "공터1", "암병원", "의과대학", None,
    "공학관", "백양로2", "백주년기념관", "안과병원", "제중관", None,
    "체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스병원",
    "중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학",
    "백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC",
    None, None, None, None, "새천년관", "이윤재관",
]

# 변수 : 함수 생성 -> 학교 지도 및 좌표 - n개의 열을 가지는 지도 생성
schoolMap = create_map(6, school_locations)

# 변수 : 설정 -> 딕셔너리 - 난이도
settings = {"difficulty": ["쉬움", "보통", "어려움"]}

if __name__ == "__main__":
    print("\n" + "=" * 40)
    print("출발! 당신은 지금 학교에 있습니다")
    print("=" * 40)
    gameplay = True
    
    while gameplay:
        user_input = input("\n이동할 방향을 입력하세요 (w/s/a/d): ")

        if user_input == "q":
            break

        move_char(user_input)
    
