-- phpMyAdmin SQL Dump
-- version 4.2.7.1
-- http://www.phpmyadmin.net
--
-- Client :  localhost
-- Généré le :  Jeu 13 Février 2025 à 21:38
-- Version du serveur :  5.6.20-log
-- Version de PHP :  5.4.31

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Base de données :  `base`
--

-- --------------------------------------------------------

--
-- Structure de la table `articles`
--

CREATE TABLE IF NOT EXISTS `articles` (
`id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `author` varchar(100) NOT NULL,
  `date_posted` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7 ;

--
-- Contenu de la table `articles`
--

INSERT INTO `articles` (`id`, `title`, `content`, `author`, `date_posted`, `image_path`) VALUES
(1, 'j''aime', 'regardez ca mes sangs ', 'teacher', 0x323032352d30322d30392032313a34353a3038, 'static/uploads/49067.jpeg'),
(2, 'svp calm down', 'Ceci est l''article de la décennie ', 'teacher', 0x323032352d30322d30392032313a35373a3537, 'static/uploads/Maurice18.jpeg'),
(3, 'uivyiiy', 'gcudltdutldl;utdf:lflvgucdolytdsikyrsrkyqsteqnfdhgdhtgdfktyeky', 'teacher', 0x323032352d30322d30392032313a35393a3032, 'static/uploads/Modified2.jpeg'),
(4, 'ljfluiydlydcxkydikydfkidfluyf', 'luyjdlmuyfdm:iyfiyèfi:lyfglu:yfvclutcdyltdxcklydytdky;uyfryfv:', 'teacher', 0x323032352d30322d30392032313a35393a3237, 'static/uploads/REUNION_17-6_23-6_6.jpeg');

-- --------------------------------------------------------

--
-- Structure de la table `devoirs`
--

CREATE TABLE IF NOT EXISTS `devoirs` (
`id` int(101) NOT NULL,
  `enonce` varchar(100) CHARACTER SET utf8 NOT NULL,
  `path` varchar(250) CHARACTER SET utf8 NOT NULL
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=16 ;

-- --------------------------------------------------------

--
-- Structure de la table `grades`
--

CREATE TABLE IF NOT EXISTS `grades` (
`id` int(11) NOT NULL,
  `teacher` varchar(255) NOT NULL,
  `student` varchar(255) NOT NULL,
  `subject` varchar(225) NOT NULL,
  `grade` varchar(100) NOT NULL
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11 ;

-- --------------------------------------------------------

--
-- Structure de la table `honeypot`
--

CREATE TABLE IF NOT EXISTS `honeypot` (
`id` int(11) NOT NULL,
  `secret_key` varchar(255) CHARACTER SET utf8 NOT NULL,
  `role` varchar(255) CHARACTER SET utf8 NOT NULL,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=24 ;

--
-- Contenu de la table `honeypot`
--

INSERT INTO `honeypot` (`id`, `secret_key`, `role`, `username`) VALUES
(1, '-w99gQhX0s6crlcWod7D/1mcVGelaGvR66Vg46fo9D6VJ6J_-+', 'admin', 'admin');

-- --------------------------------------------------------

--
-- Structure de la table `mailbox`
--

CREATE TABLE IF NOT EXISTS `mailbox` (
`id` int(11) NOT NULL,
  `sender` varchar(255) NOT NULL,
  `receiver` varchar(255) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `sent_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=25 ;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
`id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(100) NOT NULL
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=27 ;

--
-- Contenu de la table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES
(1, 'admin', '$2b$12$fpKHacImgI.PsWcA/CMK9uY5SGbJmS98tPLdsClka812eP4HzmhDu', 'admin');

--
-- Index pour les tables exportées
--

--
-- Index pour la table `articles`
--
ALTER TABLE `articles`
 ADD PRIMARY KEY (`id`);

--
-- Index pour la table `devoirs`
--
ALTER TABLE `devoirs`
 ADD PRIMARY KEY (`id`);

--
-- Index pour la table `grades`
--
ALTER TABLE `grades`
 ADD PRIMARY KEY (`id`);

--
-- Index pour la table `honeypot`
--
ALTER TABLE `honeypot`
 ADD PRIMARY KEY (`id`);

--
-- Index pour la table `mailbox`
--
ALTER TABLE `mailbox`
 ADD PRIMARY KEY (`id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
 ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables exportées
--

--
-- AUTO_INCREMENT pour la table `articles`
--
ALTER TABLE `articles`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=7;
--
-- AUTO_INCREMENT pour la table `devoirs`
--
ALTER TABLE `devoirs`
MODIFY `id` int(101) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=16;
--
-- AUTO_INCREMENT pour la table `grades`
--
ALTER TABLE `grades`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=11;
--
-- AUTO_INCREMENT pour la table `honeypot`
--
ALTER TABLE `honeypot`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=24;
--
-- AUTO_INCREMENT pour la table `mailbox`
--
ALTER TABLE `mailbox`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=25;
--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=27;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
