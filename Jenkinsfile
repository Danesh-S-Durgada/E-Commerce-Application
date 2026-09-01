pipeline {
    agent any

    environment {
        // ==========================================
        // DOCKER IMAGE NAMES
        // ==========================================
        BACKEND_IMAGE = "cloud-ecommerce-backend"
        FRONTEND_IMAGE = "cloud-ecommerce-frontend"
        IMAGE_TAG = "${BUILD_NUMBER}"

        // ==========================================
        // AWS / ECR
        // ==========================================
        AWS_REGION = "ap-south-1"
        AWS_ACCOUNT_ID = "604393641173"

        ECR_REGISTRY = "604393641173.dkr.ecr.ap-south-1.amazonaws.com"

        ECR_BACKEND =
            "604393641173.dkr.ecr.ap-south-1.amazonaws.com/cloud-ecommerce-backend"

        ECR_FRONTEND =
            "604393641173.dkr.ecr.ap-south-1.amazonaws.com/cloud-ecommerce-frontend"

        // ==========================================
        // EC2
        // ==========================================
        EC2_HOST = "3.109.200.146"
        EC2_APP_DIR = "/home/ubuntu/E-Commerce-Application"
    }

    stages {

        // =========================================================
        // 1. CHECKOUT
        // =========================================================

        stage('Checkout') {
            steps {
                echo '===== CHECKING OUT SOURCE CODE ====='
                checkout scm
            }
        }


        // =========================================================
        // 2. TEST EC2 SSH
        // =========================================================

        stage('Test EC2 SSH') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'EC2_KEY',
                        keyFileVariable: 'EC2_KEY',
                        usernameVariable: 'EC2_USER'
                    )
                ]) {

                    bat '''
                        echo ==================================================
                        echo          TESTING JENKINS TO EC2 SSH
                        echo ==================================================

                        echo User: %EC2_USER%
                        echo EC2: %EC2_HOST%

                        echo.
                        echo ===== FIXING SSH KEY PERMISSIONS =====

                        icacls "%EC2_KEY%" /inheritance:r
                        icacls "%EC2_KEY%" /grant:r "SYSTEM:(R)"

                        echo.
                        echo ===== SSH KEY PERMISSIONS =====

                        icacls "%EC2_KEY%"

                        echo.
                        echo ===== TESTING SSH CONNECTION =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "echo EC2 SSH CONNECTION SUCCESSFUL && hostname && whoami"

                        if errorlevel 1 (
                            echo.
                            echo ERROR: EC2 SSH CONNECTION FAILED
                            exit /b 1
                        )

                        echo.
                        echo ===== EC2 SSH TEST PASSED =====
                    '''
                }
            }
        }


        // =========================================================
        // 3. CHECK ENVIRONMENT
        // =========================================================

        stage('Check Environment') {
            steps {

                bat '''
                    echo ==================================================
                    echo             CHECKING JENKINS ENVIRONMENT
                    echo ==================================================

                    echo.
                    echo ===== JENKINS USER =====
                    whoami

                    echo.
                    echo ===== DOCKER =====
                    docker --version

                    if errorlevel 1 (
                        echo ERROR: DOCKER NOT AVAILABLE
                        exit /b 1
                    )

                    echo.
                    echo ===== AWS CLI =====
                    aws --version

                    if errorlevel 1 (
                        echo ERROR: AWS CLI NOT AVAILABLE
                        exit /b 1
                    )

                    echo.
                    echo ===== GIT =====
                    git --version

                    echo.
                    echo ===== NODE =====
                    docker run --rm node:22-alpine node --version

                    if errorlevel 1 (
                        echo ERROR: NODE TEST FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== PYTHON =====
                    docker run --rm python:3.11-slim python --version

                    if errorlevel 1 (
                        echo ERROR: PYTHON TEST FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== ENVIRONMENT CHECK PASSED =====
                '''
            }
        }


        // =========================================================
        // 4. BACKEND TESTS
        // =========================================================

        stage('Backend Tests') {
            steps {
                bat '''
                echo ==================================================
                echo              BACKEND TESTS
                echo ==================================================

                echo.
                echo ===== REMOVING OLD TEST DATABASE =====
                docker rm -f ecommerce-test-db 2>nul

                echo.
                echo ===== STARTING MYSQL TEST DATABASE =====

                docker run -d ^
                  --name ecommerce-test-db ^
                  -e MYSQL_ROOT_PASSWORD=root ^
                  -e MYSQL_DATABASE=ecommerce ^
                  -e MYSQL_USER=ecommerce ^
                  -e MYSQL_PASSWORD=ecommerce123 ^
                  -v "%WORKSPACE%\\docker\\mysql\\init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                  mysql:8.4

                if errorlevel 1 (
                    echo ERROR: MYSQL TEST DATABASE FAILED TO START
                    exit /b 1
                )

                echo.
                echo ===== WAITING FOR MYSQL TO BE READY =====

                :wait_mysql
                docker exec ecommerce-test-db mysqladmin ping ^
                  -h localhost ^
                  -u root ^
                  -proot ^
                  --silent >nul 2>&1

                if errorlevel 1 (
                    echo MySQL is still starting...
                    powershell -Command "Start-Sleep -Seconds 5"
                    goto wait_mysql
                )

                echo MySQL is READY

                echo.
                echo ===== VERIFYING PRODUCTS TABLE =====

                docker exec ecommerce-test-db mysql ^
                  -u ecommerce ^
                  -pecommerce123 ^
                  -e "USE ecommerce; SHOW TABLES;"

                if errorlevel 1 (
                    echo ERROR: DATABASE INITIALIZATION FAILED
                    docker logs ecommerce-test-db
                    docker rm -f ecommerce-test-db
                    exit /b 1
                )

                echo.
                echo ===== RUNNING PYTHON BACKEND TESTS =====

                docker run --rm ^
                  --link ecommerce-test-db:mysql ^
                  -e MYSQL_USER=ecommerce ^
                  -e MYSQL_PASSWORD=ecommerce123 ^
                  -e MYSQL_HOST=mysql ^
                  -e MYSQL_PORT=3306 ^
                  -e MYSQL_DATABASE=ecommerce ^
                  -v "%WORKSPACE%\\backend:/app" ^
                  -w /app ^
                  python:3.11-slim ^
                  sh -c "pip install --no-cache-dir -r requirements.txt && pytest tests -q"

                if errorlevel 1 (
                    echo.
                    echo ERROR: BACKEND TESTS FAILED
                    docker logs ecommerce-test-db
                    docker rm -f ecommerce-test-db
                    exit /b 1
                )

                echo.
                echo ===== BACKEND TESTS PASSED =====

                docker rm -f ecommerce-test-db
                '''
            }
        }


        // =========================================================
        // 5. FRONTEND BUILD
        // =========================================================

        stage('Frontend Build') {
            steps {

                bat '''
                    echo ==================================================
                    echo              FRONTEND BUILD
                    echo ==================================================

                    docker run --rm ^
                      -v "%CD%\\frontend:/app" ^
                      -w /app ^
                      node:22-alpine ^
                      sh -c "npm ci && npm run build"

                    if errorlevel 1 (
                        echo.
                        echo ERROR: FRONTEND BUILD FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== FRONTEND BUILD PASSED =====
                '''
            }
        }


        // =========================================================
        // 6. DOCKER BUILD
        // =========================================================

        stage('Docker Build') {
            steps {

                bat '''
                    echo ==================================================
                    echo              DOCKER IMAGE BUILD
                    echo ==================================================

                    echo.
                    echo ===== BUILDING BACKEND IMAGE =====

                    docker build ^
                      -t %BACKEND_IMAGE%:%IMAGE_TAG% ^
                      ./backend

                    if errorlevel 1 (
                        echo ERROR: BACKEND DOCKER BUILD FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== BUILDING FRONTEND IMAGE =====

                    docker build ^
                      -t %FRONTEND_IMAGE%:%IMAGE_TAG% ^
                      ./frontend

                    if errorlevel 1 (
                        echo ERROR: FRONTEND DOCKER BUILD FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== BUILT BACKEND IMAGE =====

                    docker images %BACKEND_IMAGE%

                    echo.
                    echo ===== BUILT FRONTEND IMAGE =====

                    docker images %FRONTEND_IMAGE%

                    echo.
                    echo ===== DOCKER BUILD PASSED =====
                '''
            }
        }


        // =========================================================
        // 7. TRIVY SECURITY SCAN
        // =========================================================

        stage('Trivy Scan') {
            steps {

                bat '''
                    echo ==================================================
                    echo              TRIVY SECURITY SCAN
                    echo ==================================================

                    echo.
                    echo ===== BACKEND IMAGE SCAN =====

                    docker run --rm ^
                      -v //var/run/docker.sock:/var/run/docker.sock ^
                      aquasec/trivy:latest ^
                      image ^
                      --exit-code 0 ^
                      --severity HIGH,CRITICAL ^
                      %BACKEND_IMAGE%:%IMAGE_TAG%

                    if errorlevel 1 (
                        echo ERROR: BACKEND TRIVY SCAN FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== FRONTEND IMAGE SCAN =====

                    docker run --rm ^
                      -v //var/run/docker.sock:/var/run/docker.sock ^
                      aquasec/trivy:latest ^
                      image ^
                      --exit-code 0 ^
                      --severity HIGH,CRITICAL ^
                      %FRONTEND_IMAGE%:%IMAGE_TAG%

                    if errorlevel 1 (
                        echo ERROR: FRONTEND TRIVY SCAN FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== TRIVY SCAN COMPLETED =====
                '''
            }
        }


        // =========================================================
        // 8. ECR LOGIN
        // =========================================================

        stage('ECR Login') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-ecr-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    bat '''
                        echo ==================================================
                        echo                 AWS ECR LOGIN
                        echo ==================================================

                        set AWS_DEFAULT_REGION=%AWS_REGION%

                        echo.
                        echo ===== AWS IDENTITY =====

                        aws sts get-caller-identity

                        if errorlevel 1 (
                            echo ERROR: AWS CREDENTIALS ARE INVALID
                            exit /b 1
                        )

                        echo.
                        echo ===== LOGIN TO ECR =====

                        aws ecr get-login-password ^
                          --region %AWS_REGION% ^
                          | docker login ^
                          --username AWS ^
                          --password-stdin %ECR_REGISTRY%

                        if errorlevel 1 (
                            echo ERROR: ECR LOGIN FAILED
                            exit /b 1
                        )

                        echo.
                        echo ===== ECR LOGIN SUCCESSFUL =====
                    '''
                }
            }
        }


        // =========================================================
        // 9. TAG IMAGES
        // =========================================================

        stage('Tag Images for ECR') {
            steps {

                bat '''
                    echo ==================================================
                    echo              TAGGING IMAGES FOR ECR
                    echo ==================================================

                    echo.
                    echo ===== BACKEND VERSION TAG =====

                    docker tag ^
                      %BACKEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_BACKEND%:%IMAGE_TAG%

                    if errorlevel 1 (
                        echo ERROR: BACKEND VERSION TAG FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== BACKEND LATEST TAG =====

                    docker tag ^
                      %BACKEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_BACKEND%:latest

                    if errorlevel 1 (
                        echo ERROR: BACKEND LATEST TAG FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== FRONTEND VERSION TAG =====

                    docker tag ^
                      %FRONTEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_FRONTEND%:%IMAGE_TAG%

                    if errorlevel 1 (
                        echo ERROR: FRONTEND VERSION TAG FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== FRONTEND LATEST TAG =====

                    docker tag ^
                      %FRONTEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_FRONTEND%:latest

                    if errorlevel 1 (
                        echo ERROR: FRONTEND LATEST TAG FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== ECR TAGGING COMPLETED =====
                '''
            }
        }


        // =========================================================
        // 10. PUSH TO ECR
        // =========================================================

        stage('Push Images to ECR') {
            steps {

                bat '''
                    echo ==================================================
                    echo               PUSHING IMAGES TO ECR
                    echo ==================================================

                    echo.
                    echo ===== PUSHING BACKEND VERSION =====

                    docker push %ECR_BACKEND%:%IMAGE_TAG%

                    if errorlevel 1 (
                        echo ERROR: BACKEND VERSION PUSH FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== PUSHING BACKEND LATEST =====

                    docker push %ECR_BACKEND%:latest

                    if errorlevel 1 (
                        echo ERROR: BACKEND LATEST PUSH FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== PUSHING FRONTEND VERSION =====

                    docker push %ECR_FRONTEND%:%IMAGE_TAG%

                    if errorlevel 1 (
                        echo ERROR: FRONTEND VERSION PUSH FAILED
                        exit /b 1
                    )

                    echo.
                    echo ===== PUSHING FRONTEND LATEST =====

                    docker push %ECR_FRONTEND%:latest

                    if errorlevel 1 (
                        echo ERROR: FRONTEND LATEST PUSH FAILED
                        exit /b 1
                    )

                    echo.
                    echo ==================================================
                    echo             ECR PUSH COMPLETED
                    echo ==================================================
                '''
            }
        }


        // =========================================================
        // 11. DEPLOY TO EC2
        // =========================================================

        stage('Deploy to EC2') {

            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'EC2_KEY',
                        keyFileVariable: 'EC2_KEY',
                        usernameVariable: 'EC2_USER'
                    )
                ]) {

                    bat '''
                        echo ==================================================
                        echo             DEPLOYING TO EC2
                        echo ==================================================

                        echo.
                        echo ===== FIXING SSH KEY PERMISSIONS =====

                        icacls "%EC2_KEY%" /inheritance:r
                        icacls "%EC2_KEY%" /grant:r "SYSTEM:(R)"

                        echo.
                        echo ===== TESTING SSH CONNECTION =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "echo SSH CONNECTION SUCCESSFUL"

                        if errorlevel 1 (
                            echo ERROR: SSH CONNECTION FAILED
                            exit /b 1
                        )


                        echo.
                        echo ===== CHECKING EC2 DOCKER =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "docker --version && docker compose version"

                        if errorlevel 1 (
                            echo ERROR: DOCKER OR DOCKER COMPOSE NOT AVAILABLE
                            exit /b 1
                        )


                        echo.
                        echo ===== CHECKING APPLICATION DIRECTORY =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "test -f %EC2_APP_DIR%/docker-compose.yml"

                        if errorlevel 1 (
                            echo ERROR: docker-compose.yml NOT FOUND
                            exit /b 1
                        )


                        echo.
                        echo ===== LOGIN TO ECR ON EC2 =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %ECR_REGISTRY%"

                        if errorlevel 1 (
                            echo ERROR: EC2 ECR LOGIN FAILED
                            exit /b 1
                        )


                        echo.
                        echo ===== PULLING NEW BACKEND IMAGE =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "docker pull %ECR_BACKEND%:latest"

                        if errorlevel 1 (
                            echo ERROR: BACKEND IMAGE PULL FAILED
                            exit /b 1
                        )


                        echo.
                        echo ===== PULLING NEW FRONTEND IMAGE =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "docker pull %ECR_FRONTEND%:latest"

                        if errorlevel 1 (
                            echo ERROR: FRONTEND IMAGE PULL FAILED
                            exit /b 1
                        )


                        echo.
                        echo ===== DOCKER COMPOSE PULL =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "cd %EC2_APP_DIR% && docker compose pull"

                        if errorlevel 1 (
                            echo ERROR: DOCKER COMPOSE PULL FAILED
                            exit /b 1
                        )


                        echo.
                        echo ===== DEPLOYING APPLICATION =====

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "cd %EC2_APP_DIR% && docker compose up -d"

                        if errorlevel 1 (
                            echo ERROR: DOCKER COMPOSE DEPLOYMENT FAILED
                            exit /b 1
                        )


                        echo.
                        echo ===== WAITING FOR CONTAINERS =====

                        timeout /t 15 /nobreak


                        echo.
                        echo ==================================================
                        echo           CHECKING CONTAINER STATUS
                        echo ==================================================

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "cd %EC2_APP_DIR% && docker compose ps"

                        if errorlevel 1 (
                            echo ERROR: DOCKER COMPOSE STATUS CHECK FAILED
                            exit /b 1
                        )


                        echo.
                        echo ==================================================
                        echo           WAITING FOR MYSQL HEALTH
                        echo ==================================================

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "bash -c 'for i in {1..30}; do status=$(docker inspect -f \"{{.State.Health.Status}}\" ecommerce-mysql 2>/dev/null || true); echo MYSQL_STATUS=$status; if [ \"$status\" = \"healthy\" ]; then exit 0; fi; sleep 5; done; echo MYSQL HEALTH CHECK FAILED; exit 1'"

                        if errorlevel 1 (
                            echo.
                            echo ERROR: MYSQL DID NOT BECOME HEALTHY

                            ssh -i "%EC2_KEY%" ^
                              -o StrictHostKeyChecking=no ^
                              -o UserKnownHostsFile=NUL ^
                              %EC2_USER%@%EC2_HOST% ^
                              "docker logs --tail 100 ecommerce-mysql"

                            exit /b 1
                        )


                        echo.
                        echo ==================================================
                        echo           WAITING FOR BACKEND HEALTH
                        echo ==================================================

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "bash -c 'for i in {1..30}; do status=$(docker inspect -f \"{{.State.Health.Status}}\" ecommerce-backend 2>/dev/null || true); echo BACKEND_STATUS=$status; if [ \"$status\" = \"healthy\" ]; then exit 0; fi; sleep 5; done; echo BACKEND HEALTH CHECK FAILED; exit 1'"

                        if errorlevel 1 (
                            echo.
                            echo ERROR: BACKEND DID NOT BECOME HEALTHY

                            echo ===== BACKEND LOGS =====

                            ssh -i "%EC2_KEY%" ^
                              -o StrictHostKeyChecking=no ^
                              -o UserKnownHostsFile=NUL ^
                              %EC2_USER%@%EC2_HOST% ^
                              "docker logs --tail 100 ecommerce-backend"

                            exit /b 1
                        )


                        echo.
                        echo ==================================================
                        echo            VERIFYING BACKEND /health
                        echo ==================================================

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "curl -fsS http://127.0.0.1:8000/health"

                        if errorlevel 1 (
                            echo ERROR: BACKEND /health CHECK FAILED

                            ssh -i "%EC2_KEY%" ^
                              -o StrictHostKeyChecking=no ^
                              -o UserKnownHostsFile=NUL ^
                              %EC2_USER%@%EC2_HOST% ^
                              "docker logs --tail 100 ecommerce-backend"

                            exit /b 1
                        )


                        echo.
                        echo ==================================================
                        echo            VERIFYING FRONTEND
                        echo ==================================================

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "curl -fsS -I http://127.0.0.1:4200"

                        if errorlevel 1 (
                            echo ERROR: FRONTEND HEALTH CHECK FAILED

                            ssh -i "%EC2_KEY%" ^
                              -o StrictHostKeyChecking=no ^
                              -o UserKnownHostsFile=NUL ^
                              %EC2_USER%@%EC2_HOST% ^
                              "docker logs --tail 100 ecommerce-frontend"

                            exit /b 1
                        )


                        echo.
                        echo ==================================================
                        echo             FINAL CONTAINER STATUS
                        echo ==================================================

                        ssh -i "%EC2_KEY%" ^
                          -o StrictHostKeyChecking=no ^
                          -o UserKnownHostsFile=NUL ^
                          %EC2_USER%@%EC2_HOST% ^
                          "cd %EC2_APP_DIR% && docker compose ps"


                        echo.
                        echo ==================================================
                        echo          DEPLOYMENT SUCCESSFUL
                        echo ==================================================
                        echo Backend:  HEALTHY
                        echo Frontend: HEALTHY
                        echo MySQL:    HEALTHY
                        echo ==================================================
                    '''
                }
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {
            echo '''
==================================================
       CI/CD PIPELINE COMPLETED SUCCESSFULLY
==================================================
Docker images:
    Backend  -> AWS ECR
    Frontend -> AWS ECR

Deployment:
    EC2 -> SUCCESS

Health:
    MySQL    -> HEALTHY
    Backend  -> HEALTHY
    Frontend -> VERIFIED

==================================================
'''
        }

        failure {
            echo '''
==================================================
             CI/CD PIPELINE FAILED
==================================================

One or more stages failed.

Check the Jenkins Console Output to identify
the failed stage.

If deployment failed, check:
    - EC2 SSH
    - ECR login
    - Docker image pull
    - Docker Compose
    - MySQL health
    - Backend health
    - Frontend health

==================================================
'''
        }

        always {

            bat '''
                echo ==================================================
                echo          JENKINS FINAL IMAGE STATUS
                echo ==================================================

                echo.
                echo ===== LOCAL BACKEND IMAGES =====
                docker images cloud-ecommerce-backend

                echo.
                echo ===== LOCAL FRONTEND IMAGES =====
                docker images cloud-ecommerce-frontend

                echo.
                echo ===== ECR BACKEND IMAGES =====
                docker images %ECR_BACKEND%

                echo.
                echo ===== ECR FRONTEND IMAGES =====
                docker images %ECR_FRONTEND%

                echo.
                echo ===== PIPELINE FINISHED =====
            '''
        }
    }
}

