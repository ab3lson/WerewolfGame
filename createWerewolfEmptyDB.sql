-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Feb 13, 2020 at 08:13 PM
-- Server version: 10.0.28-MariaDB-2+b1
-- PHP Version: 7.3.11-1~deb10u1

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
  `UserId` int(11) NOT NULL,
  `Round` int(11) NOT NULL,
  `IsAlive` tinyint(4) NOT NULL,
  `RoomId` int(11) NOT NULL,
  `RoleId` int(11) NOT NULL,
  `KillVotes` int(11) NOT NULL,
  `IsGameLive` tinyint(4) NOT NULL,
  `DecisionTimer` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Lobby`
--

CREATE TABLE `Lobby` (
  `PlayersNeeded` int(11) NOT NULL,
  `ID` int(11) NOT NULL,
  `RoomId` text NOT NULL,
  `DecisionTimer` int(11) NOT NULL,
  `CurrentPlayers` int(11) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Roles`
--

CREATE TABLE `Roles` (
  `RoleId` int(11) NOT NULL,
  `RoleName` varchar(50) NOT NULL,
  `RoleDescription` varchar(1000) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
  ADD PRIMARY KEY (`UserId`);

--
-- Indexes for table `Lobby`
--
ALTER TABLE `Lobby`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `Roles`
--
ALTER TABLE `Roles`
  ADD PRIMARY KEY (`RoleId`);

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
-- AUTO_INCREMENT for table `Lobby`
--
ALTER TABLE `Lobby`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `Roles`
--
ALTER TABLE `Roles`
  MODIFY `RoleId` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `User`
--
ALTER TABLE `User`
  MODIFY `UserId` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
