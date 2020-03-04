-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Mar 04, 2020 at 02:05 PM
-- Server version: 5.7.28-0ubuntu0.18.04.4
-- PHP Version: 7.2.24-0ubuntu0.18.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `werewolf`
--

-- --------------------------------------------------------

--
-- Table structure for table `ActiveGames`
--

CREATE TABLE `ActiveGames` (
  `Username` varchar(50) NOT NULL,
  `Round` int(11) NOT NULL DEFAULT '0',
  `IsAlive` tinyint(4) NOT NULL DEFAULT '1',
  `RoomId` varchar(4) NOT NULL,
  `Role` varchar(12) NOT NULL,
  `KillVotes` int(11) NOT NULL DEFAULT '0',
  `IsGameLive` tinyint(4) NOT NULL DEFAULT '1',
  `DecisionTimer` int(11) NOT NULL,
  `ActiveGameID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Lobby`
--

CREATE TABLE `Lobby` (
  `PlayersNeeded` int(11) NOT NULL,
  `ID` int(11) NOT NULL,
  `RoomId` varchar(4) NOT NULL,
  `DecisionTimer` int(11) NOT NULL,
  `CurrentPlayers` int(11) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Roles`
--

CREATE TABLE `Roles` (
  `Role` varchar(50) NOT NULL,
  `RoleDescription` varchar(1000) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `Roles`
--

INSERT INTO `Roles` (`Role`, `RoleDescription`) VALUES
('headWerewolf', 'Each night, you will select a villager to be killed.'),
('healer', 'Each night, you will choose one player to be immune to a werewolf attack.'),
('seer', 'Each night, you will be able to see the role of one player of your choosing.'),
('villager', 'Your role is to determine who the werewolf is and chase them out.'),
('werewolf', 'Each night, you will head werewolf decide who to kill.');

-- --------------------------------------------------------

--
-- Table structure for table `Stats`
--

CREATE TABLE `Stats` (
  `UserId` int(11) NOT NULL,
  `GamesPlayed` int(11) NOT NULL DEFAULT '0',
  `GamesWon` int(11) NOT NULL DEFAULT '0',
  `PeopleEaten` int(11) NOT NULL DEFAULT '0',
  `PeopleSaved` int(11) NOT NULL DEFAULT '0',
  `TimesWerewolf` int(11) NOT NULL DEFAULT '0',
  `TimesHunter` int(11) NOT NULL DEFAULT '0',
  `TimesDoctor` int(11) NOT NULL DEFAULT '0',
  `TimesSeer` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE `User` (
  `UserId` int(11) NOT NULL,
  `Username` varchar(50) DEFAULT 'Guest',
  `Password` varchar(50) DEFAULT NULL,
  `Email` varchar(50) DEFAULT NULL,
  `IsGuest` tinyint(4) NOT NULL,
  `LoggedIn` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table used to define ';

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ActiveGames`
--
ALTER TABLE `ActiveGames`
  ADD PRIMARY KEY (`ActiveGameID`);

--
-- Indexes for table `Lobby`
--
ALTER TABLE `Lobby`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `Roles`
--
ALTER TABLE `Roles`
  ADD PRIMARY KEY (`Role`);

--
-- Indexes for table `Stats`
--
ALTER TABLE `Stats`
  ADD PRIMARY KEY (`UserId`);

--
-- Indexes for table `User`
--
ALTER TABLE `User`
  ADD PRIMARY KEY (`UserId`),
  ADD UNIQUE KEY `Username` (`Username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ActiveGames`
--
ALTER TABLE `ActiveGames`
  MODIFY `ActiveGameID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;
--
-- AUTO_INCREMENT for table `Lobby`
--
ALTER TABLE `Lobby`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT for table `User`
--
ALTER TABLE `User`
  MODIFY `UserId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
