# API de Gestion Scolaire (Type Pronote)

## Description
Cette API permet la gestion d'un système scolaire similaire à Pronote. Elle est développée en Flask avec une base de données MySQL sur Uwamp. Elle offre différentes fonctionnalités pour les professeurs, les élèves et l'administrateur.

## Installation

1. **Téléchargez et installez Uwamp** si ce n'est pas déjà fait.
2. **Clonez ce dépôt** dans le répertoire www du dossier Uwamp :
   ```sh
   git clone https://github.com/Bruburnono/DevSecOps.git
   ```
3. **Lancement du serveur Uwamp** :
   ```
   ```
4. **Installez les dépendances** :
   ```sh
   pip install -r requirements.txt
   ```
5. **Importez la base de données** dans MySQL via phpMyAdmin 
   ```
   ```
6. **Lancez l'application Flask** :
   ```sh
   python app.py ou python3 app.py
   ```
7 ** localhost:5000 dans navigateur

## Fonctionnalités

### Pour les Professeurs
- Ajout et consultation des notes des élèves
- Création de devoirs
- Publication d'articles visibles sur la page d'accueil
- Consultation et envoi de messages via la messagerie interne

- Consultation de l'agenda

### Pour les Étudiants
- Consultation des notes
- Consultation des devoirs
- Consultation des articles publiés
- Consultation et envoi de messages via la messagerie interne
- Consultation de l'agenda

### Pour l'Administrateur
- Accès à toutes les fonctionnalités disponibles
- Ajout et suppression d'utilisateurs
- Modification des rôles des utilisateurs
- Consultation de l'agenda

## Sécurité
- Protection contre les injections SQL
- Hachage sécurisé des mots de passe (bcrypt)
- Vérification des fichiers importés
- Gestion des sessions avec une clé sécurisée

## API Endpoints
| Méthode | Endpoint | Description |
|---------|---------|-------------|
| `POST` | `/login` | Authentification utilisateur |
| `POST` | `/dashboard_admin` | Création d'un nouvel utilisateur |
| `GET` | `/grades` | Consultation des notes d'un élève |
| `POST` | `/grades` | Ajout de notes (professeur uniquement) |
| `GET` | `/devoirs` | Consultation des devoirs |
| `POST` | `/devoirs` | Création de devoirs (professeur uniquement) |
| `GET` | `/` | Consultation des articles et la main page|
| `POST` | `/write_article` | Ajout d'articles (professeur uniquement) |
| `GET` | `/mailbox` | Consultation des messages |
| `POST` | `/mailbox` | Envoi d'un message |
| `POST` | `/dashboard_admin` | Gestion des utilisateurs (ajout, suppression, modification de rôle) |

## Auteurs
- **2e années Guardia, groupe des cracks** - *Développement et maintenance* - [GitHub](https://github.com/Bruburnono)

## Licence
C'est os amusez vous :) 

