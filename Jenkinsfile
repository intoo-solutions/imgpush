#!/usr/bin/env groovy

// Ne garder que 5 builds et 5 artefacts
properties([buildDiscarder(logRotator(artifactNumToKeepStr: '5', numToKeepStr: '5'))])

node {
	 
	stage('checkout'){
		git branch: 'feature/uuid', url: 'https://github.com/pdelaby/imgpush'
	}
	
	// Ajouter un système de tags
    stage('build docker') {
        docker.build("intoo/imgpush:latest", '.')
    }
}