pipeline {
  agent any

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

    stage('Backend Tests') {
      steps {
        sh '''
          python3 -m venv .ci-venv
          . .ci-venv/bin/activate
          pip install -r backend/requirements.txt
          pytest backend/tests -q
        '''
      }
    }

    stage('Frontend Build') {
      steps {
        sh '''
          cd frontend
          npm install
          npm run build
        '''
      }
    }

    stage('Docker Build') {
      steps {
        sh '''
          docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend
          docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend
        '''
      }
    }

    stage('Trivy Scan') {
      steps {
        sh '''
          trivy image --exit-code 0 --severity HIGH,CRITICAL ${BACKEND_IMAGE}:${IMAGE_TAG}
          trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE}:${IMAGE_TAG}
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
  }
}
