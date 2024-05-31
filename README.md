## 입출금 프로젝트

1. 대규모 데이터를 관리하기위해 cqrs 패턴으로 책임을 분리.
2. 무결성을 유지하기위해 이벤트소싱을 통해 디비를 동기화
3. (명령 서버)동시성 문제를 해결하기위해 트랜잭션을 일정한 단위로 조절
4. (조회 서버)단일 인덱싱과 복합인덱싱으로 검색을 최적화
5. (조회 서버)레디스 캐싱을 사용해 빠른 응답속도를 제공
6. (조회 서버)탐색이 빠른 커서페이지네이션과 특정페이지 이동을위한 오프셋을 동시에사용

## 설치

1. **저장소 클론:**
   ```sh
   git clone <repository-url>
   cd banking_system
   ```

2. **가상 환경 생성 및 활성화:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # 윈도우의 경우 `venv\Scriptsctivate`
   ```

3. **의존성 설치:**
   ```sh
   pip install -r query_server/requirements.txt
   ```

4. **마이그레이션 적용:**
   ```sh
   cd query_server
   cd command_server

   python manage.py makemigration
   python manage.py migrate
   ```

5. **슈퍼유저 생성:**
   ```sh
   python manage.py createsuperuser
   ```

6. **개발 서버 실행:**
   ```sh
   python manage.py runserver
   ```
7. **도커 컴포즈 실행:**
   ```sh
   docker-compose up -build -d
   ```
8.  **컨슈머 실행:**
   ```sh
   python query_server/manage.py consumer
   ```