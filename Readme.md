# Movie Auth service 
Authorise backend service for frontend movie service. 

pr on async_api: 

Install:

```bash
# clone repo
git clone https://github.com/AlexanderNiMo/auth_s_1.git
cd Async_API_sprint_1

```

Configure:

 - AUTH: add file local.cfg to ./src/ (based on local_example.cfg)
 - Configure .env file based on .env_example
 

Run in dev mode:

```bash
# install requirements on host
pip install -r ./src/requirements.txt
# Run suppliers services  
docker-compose -f ./docker-compose.base.yaml -f ./docker-compose.dev.yaml up --build
# Run api app on host
python ./src/main.py
```

Run in prod mode:

```bash 
# Run service
docker-compose -f ./docker-compose.base.yaml -f ./docker-compose.prod.yaml up --build -d
```

Api will start on localhost:5000/api/v1/
Swagger app definitions location http://localhost:5000/api/docs/

Run tests:
```bash 
# Run service
docker-compose -f ./docker-compose.base.yaml -f ./src/tests/functional/docker-compose.test.yaml up --build -d
docker logs auth_tester
```