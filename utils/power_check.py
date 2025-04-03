import psutil

# 시스템 전원 상태 확인
def check_power():
    try: 
        battery = psutil.sensors_battery()
        if battery is not None:
            print(f"현재 배터리 상태: {battery.percent}%")
            return battery.power_plugged or battery.percent > 0
        else:
            # print("배터리 정보를 찾을 수 없습니다.")
            return 1  # 배터리 정보 없는 경우(데스크톱 등) 전원 ON 상태로 간주
    except Exception as e:
        print(f"오류 발생: {e}")
        return 0  # OFF 상태로 간주

