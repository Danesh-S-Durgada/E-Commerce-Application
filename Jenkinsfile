// pipeline {
//   agent any

//   environment {
//     BACKEND_IMAGE = "cloud-ecommerce-backend"
//     FRONTEND_IMAGE = "cloud-ecommerce-frontend"
//     IMAGE_TAG = "${BUILD_NUMBER}"
//   }

//   stages {
//     stage('Checkout') {
//       steps {
//         checkout scm
//       }
//     }

//     stage('Backend Tests') {
//       steps {
//         sh '''
//           python3 -m venv .ci-venv
//           . .ci-venv/bin/activate
//           pip install -r backend/requirements.txt
//           pytest backend/tests -q
//         '''
//       }
//     }

//     stage('Frontend Build') {
//       steps {
//         sh '''
//           cd frontend
//           npm install
//           npm run build
//         '''
//       }
//     }

//     stage('Docker Build') {
//       steps {
//         sh '''
//           docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend
//           docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend
//         '''
//       }
//     }

//     stage('Trivy Scan') {
//       steps {
//         sh '''
//           trivy image --exit-code 0 --severity HIGH,CRITICAL ${BACKEND_IMAGE}:${IMAGE_TAG}
//           trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE}:${IMAGE_TAG}
//         '''
//       }
//     }
//   }

//   post {
//     success {
//       echo 'CI pipeline completed successfully.'
//     }
//     failure {
//       echo 'CI pipeline failed.'
//     }
//   }
// }
pipeline {
agent any

```
environment {
    BACKEND_IMAGE = "cloud-ecommerce-backend"
    FRONTEND_IMAGE = "cloud-ecommerce-frontend"
    IMAGE_TAG = "${BUILD_NUMBER}"
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
                echo ===== BACKEND TESTS =====

                docker run --rm ^
                  -v "%CD%\\backend:/app" ^
                  -w /app ^
                  python:3.11-slim ^
                  sh -c "pip install --no-cache-dir -r requirements.txt && pytest tests -q"
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
                  sh -c "npm install && npm run build"
            '''
        }
    }

    stage('Docker Build') {
        steps {
            bat '''
                echo ===== BUILDING BACKEND IMAGE =====
                docker build -t %BACKEND_IMAGE%:%IMAGE_TAG% ./backend

                echo ===== BUILDING FRONTEND IMAGE =====
                docker build -t %FRONTEND_IMAGE%:%IMAGE_TAG% ./frontend

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
                  -v /var/run/docker.sock:/var/run/docker.sock ^
                  aquasec/trivy:latest ^
                  image --exit-code 0 --severity HIGH,CRITICAL %BACKEND_IMAGE%:%IMAGE_TAG%

                echo ===== FRONTEND IMAGE SCAN =====

                docker run --rm ^
                  -v /var/run/docker.sock:/var/run/docker.sock ^
                  aquasec/trivy:latest ^
                  image --exit-code 0 --severity HIGH,CRITICAL %FRONTEND_IMAGE%:%IMAGE_TAG%
            '''
        }
    }
}

post {
    success {
        echo 'CI pipeline completed successfully.'
    }

    failure {
        echo 'CI pipeline failed.'
    }

    always {
        bat '''
            echo ===== BACKEND IMAGES =====
            docker images cloud-ecommerce-backend

            echo ===== FRONTEND IMAGES =====
            docker images cloud-ecommerce-frontend
        '''
    }
}
```

}

