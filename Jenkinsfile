pipeline {
  agent any
  environment {
    ID = "${env.GIT_BRANCH}-${env.BUILD_ID}";
  }
  stages {
    stage('Build') {
      steps {
        sh 'docker-compose -p $ID build'
      }
    }
    stage('Test Django') {
      steps {
        sh 'mkdir reports && chmod 777 reports'
        sh 'docker-compose -f docker-compose.yml -f test-compose.yml -p $ID run interfaceserver ./run_tests.sh || true'
        junit 'reports/junit.xml'
        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
      }
    }
    stage('Test React') {
      steps {
        sh 'mkdir -p reports && chmod 777 reports'
        sh 'docker-compose -f docker-compose.yml -f test-compose.yml -p $ID run reactserver npm run test || true'
        junit 'reports/js-xunit.xml'
      }
    }
    stage('Publish') {
      when {
        branch 'master'
      }
      steps {
        sh 'docker tag seandooher/ohqueue:$ID seandooher/ohqueue:latest'
        sh 'docker push seandooher/ohqueue:latest'
      }
    }
  }
  post {
    always {
      sh 'docker-compose -p $ID down -v'
      sh 'docker container prune -f'
      sh 'docker network prune -f'
     }
  }
}
