-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Feb 26, 2020 at 02:44 PM
-- Server version: 5.7.29-0ubuntu0.18.04.1
-- PHP Version: 7.2.24-0ubuntu0.18.04.2

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

--
-- Dumping data for table `Roles`
--

INSERT INTO `Roles` (`RoleId`, `RoleName`, `RoleDescription`) VALUES
(1, 'villager', 'Your role is to determine who the werewolf is and chase them out.'),
(2, 'seer', 'During the night phase you will choose one person.\r\nIt will be revealed to you whether they are a werewolf or not.\r\n'),
(3, 'healer', 'During the night phase you will choose one person.\r\nThat person will be protected from being killed by the werewolf.\r\n'),
(4, 'werewolf', 'During the night phase you will select one person.\r\nThat person will be killed.\r\nIf there are multiple Werewolves, you will decide together who to kill.\r\n');

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

--
-- Dumping data for table `Stats`
--

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
-- Dumping data for table `User`
--

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ActiveGames`
--
ALTER TABLE `ActiveGames`
  ADD PRIMARY KEY (`Username`);

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
  MODIFY `RoleId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `User`
--
ALTER TABLE `User`
  MODIFY `UserId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

