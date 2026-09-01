pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "cloud-ecommerce-backend"
        FRONTEND_IMAGE = "cloud-ecommerce-frontend"
        IMAGE_TAG = "${BUILD_NUMBER}"

        AWS_REGION = "ap-south-1"
        AWS_ACCOUNT_ID = "604393641173"

        ECR_BACKEND = "604393641173.dkr.ecr.ap-south-1.amazonaws.com/cloud-ecommerce-backend"
        ECR_FRONTEND = "604393641173.dkr.ecr.ap-south-1.amazonaws.com/cloud-ecommerce-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Environment') {
            steps {
                bat '''
                    echo ===== JENKINS USER =====
                    whoami

                    echo ===== DOCKER =====
                    docker --version

                    echo ===== AWS CLI =====
                    aws --version

                    echo ===== GIT =====
                    git --version

                    echo ===== NODE =====
                    docker run --rm node:22-alpine node --version

                    echo ===== PYTHON =====
                    docker run --rm python:3.11-slim python --version
                '''
            }
        }

        stage('Backend Tests') {
            steps {
                bat '''
                    echo ===== STARTING TEST DATABASE =====

                    docker rm -f ecommerce-test-db 2>nul

                    docker run -d ^
                      --name ecommerce-test-db ^
                      -e MYSQL_ROOT_PASSWORD=root ^
                      -e MYSQL_DATABASE=ecommerce ^
                      -e MYSQL_USER=ecommerce ^
                      -e MYSQL_PASSWORD=ecommerce123 ^
                      mysql:8.4

                    echo ===== WAITING FOR MYSQL =====
                    timeout /t 30 /nobreak

                    echo ===== RUNNING BACKEND TESTS =====

                    docker run --rm ^
                      --link ecommerce-test-db:mysql ^
                      -e MYSQL_USER=ecommerce ^
                      -e MYSQL_PASSWORD=ecommerce123 ^
                      -e MYSQL_HOST=mysql ^
                      -e MYSQL_PORT=3306 ^
                      -e MYSQL_DATABASE=ecommerce ^
                      -v "%CD%\\backend:/app" ^
                      -w /app ^
                      python:3.11-slim ^
                      sh -c "pip install --no-cache-dir -r requirements.txt && pytest tests -q"

                    echo ===== CLEANING TEST DATABASE =====
                    docker rm -f ecommerce-test-db
                '''
            }
        }

        stage('Frontend Build') {
            steps {
                bat '''
                    echo ===== FRONTEND BUILD =====

                    docker run --rm ^
                      -v "%CD%\\frontend:/app" ^
                      -w /app ^
                      node:22-alpine ^
                      sh -c "npm ci && npm run build"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                bat '''
                    echo ===== BUILDING BACKEND IMAGE =====

                    docker build ^
                      -t %BACKEND_IMAGE%:%IMAGE_TAG% ^
                      ./backend

                    echo ===== BUILDING FRONTEND IMAGE =====

                    docker build ^
                      -t %FRONTEND_IMAGE%:%IMAGE_TAG% ^
                      ./frontend

                    echo ===== BUILT IMAGES =====

                    docker images %BACKEND_IMAGE%
                    docker images %FRONTEND_IMAGE%
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                bat '''
                    echo ===== BACKEND IMAGE SCAN =====

                    docker run --rm ^
                      -v //var/run/docker.sock:/var/run/docker.sock ^
                      aquasec/trivy:latest ^
                      image --exit-code 0 --severity HIGH,CRITICAL ^
                      %BACKEND_IMAGE%:%IMAGE_TAG%

                    echo ===== FRONTEND IMAGE SCAN =====

                    docker run --rm ^
                      -v //var/run/docker.sock:/var/run/docker.sock ^
                      aquasec/trivy:latest ^
                      image --exit-code 0 --severity HIGH,CRITICAL ^
                      %FRONTEND_IMAGE%:%IMAGE_TAG%
                '''
            }
        }
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
                        echo ===== AWS ECR LOGIN =====

                        set AWS_DEFAULT_REGION=%AWS_REGION%

                        aws sts get-caller-identity

                        aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com
                    '''
                }
            }
        }

        stage('Tag Images for ECR') {
            steps {
                bat '''
                    echo ===== TAGGING BACKEND IMAGE =====

                    docker tag ^
                      %BACKEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_BACKEND%:%IMAGE_TAG%

                    docker tag ^
                      %BACKEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_BACKEND%:latest

                    echo ===== TAGGING FRONTEND IMAGE =====

                    docker tag ^
                      %FRONTEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_FRONTEND%:%IMAGE_TAG%

                    docker tag ^
                      %FRONTEND_IMAGE%:%IMAGE_TAG% ^
                      %ECR_FRONTEND%:latest

                    echo ===== ECR TAGGED IMAGES =====

                    docker images %ECR_BACKEND%
                    docker images %ECR_FRONTEND%
                '''
            }
        }

        stage('Push Images to ECR') {
            steps {
                bat '''
                    echo ===== PUSHING BACKEND IMAGE =====

                    docker push %ECR_BACKEND%:%IMAGE_TAG%
                    docker push %ECR_BACKEND%:latest

                    echo ===== PUSHING FRONTEND IMAGE =====

                    docker push %ECR_FRONTEND%:%IMAGE_TAG%
                    docker push %ECR_FRONTEND%:latest

                    echo ===== ECR PUSH COMPLETED =====
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
            echo 'Docker images successfully pushed to AWS ECR.'
        }

        failure {
            echo 'CI/CD pipeline failed.'
        }

        always {
            bat '''
                echo ===== LOCAL BACKEND IMAGES =====
                docker images cloud-ecommerce-backend

                echo ===== LOCAL FRONTEND IMAGES =====
                docker images cloud-ecommerce-frontend

                echo ===== ECR BACKEND IMAGES =====
                docker images %ECR_BACKEND%

                echo ===== ECR FRONTEND IMAGES =====
                docker images %ECR_FRONTEND%
            '''
        }
    }
}