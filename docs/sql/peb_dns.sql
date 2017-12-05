-- MySQL dump 10.13  Distrib 5.6.30, for linux-glibc2.5 (x86_64)
--
-- Host: 10.59.87.3    Database: peb_dns_test_db2
-- ------------------------------------------------------
-- Server version	5.7.11-pingan-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED='b52b4c01-9b29-11e6-96b8-fa163edaed56:1-1936';

--
-- Table structure for table `account_local_auth`
--

DROP TABLE IF EXISTS `account_local_auth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_local_auth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_account_local_auth_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_local_auth`
--

LOCK TABLES `account_local_auth` WRITE;
/*!40000 ALTER TABLE `account_local_auth` DISABLE KEYS */;
INSERT INTO `account_local_auth` VALUES (1,'admin','pbkdf2:sha256:50000$i2oNCJgA$e7363c2c738997e2e6c7e5a46bfb616b60e5a10f6e89062867d3e680926eb13f','xxxx@gmail.com');
/*!40000 ALTER TABLE `account_local_auth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_privilege`
--

DROP TABLE IF EXISTS `account_privilege`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_privilege` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `operation` int(11) DEFAULT NULL,
  `resource_type` varchar(64) DEFAULT NULL,
  `resource_id` int(11) DEFAULT NULL,
  `comment` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_privilege_resource_id` (`resource_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_privilege`
--

LOCK TABLES `account_privilege` WRITE;
/*!40000 ALTER TABLE `account_privilege` DISABLE KEYS */;
INSERT INTO `account_privilege` VALUES (1,'SERVER_ADD',NULL,NULL,NULL,NULL),(2,'ZONE_ADD',NULL,NULL,NULL,NULL),(3,'VIEW_ADD',NULL,NULL,NULL,NULL),(4,'BIND_CONF_EDIT',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `account_privilege` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_role`
--

DROP TABLE IF EXISTS `account_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_role`
--

LOCK TABLES `account_role` WRITE;
/*!40000 ALTER TABLE `account_role` DISABLE KEYS */;
INSERT INTO `account_role` VALUES (1,'admin'),(2,'server_admin'),(3,'server_guest'),(4,'view_admin'),(5,'view_guest'),(6,'zone_admin'),(7,'zone_guest');
/*!40000 ALTER TABLE `account_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_role_privilege`
--

DROP TABLE IF EXISTS `account_role_privilege`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_role_privilege` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) DEFAULT NULL,
  `privilege_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_role_privilege_privilege_id` (`privilege_id`),
  KEY `ix_account_role_privilege_role_id` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_role_privilege`
--

LOCK TABLES `account_role_privilege` WRITE;
/*!40000 ALTER TABLE `account_role_privilege` DISABLE KEYS */;
INSERT INTO `account_role_privilege` VALUES (1,1,1),(2,2,1),(3,1,2),(4,6,2),(5,1,3),(6,4,3),(7,1,4);
/*!40000 ALTER TABLE `account_role_privilege` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_user`
--

DROP TABLE IF EXISTS `account_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `chinese_name` varchar(64) DEFAULT NULL,
  `cellphone` varchar(64) DEFAULT NULL,
  `actived` tinyint(1) DEFAULT NULL,
  `position` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `acitve` int(11) DEFAULT NULL,
  `member_since` datetime DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_account_user_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_user`
--

LOCK TABLES `account_user` WRITE;
/*!40000 ALTER TABLE `account_user` DISABLE KEYS */;
INSERT INTO `account_user` VALUES (1,'xxxx@gmail.com','admin','','',0,'','',1,'2017-12-05 15:50:23','2017-12-05 15:50:23'),(2,'','LIJIAJIA873','','',0,'','',1,'2017-12-05 15:55:43','2017-12-05 15:55:43');
/*!40000 ALTER TABLE `account_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_user_role`
--

DROP TABLE IF EXISTS `account_user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_user_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_user_role_role_id` (`role_id`),
  KEY `ix_account_user_role_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_user_role`
--

LOCK TABLES `account_user_role` WRITE;
/*!40000 ALTER TABLE `account_user_role` DISABLE KEYS */;
INSERT INTO `account_user_role` VALUES (1,1,1);
/*!40000 ALTER TABLE `account_user_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('ae93dc48247a');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dns_operation_log`
--

DROP TABLE IF EXISTS `dns_operation_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dns_operation_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operation_time` datetime DEFAULT NULL,
  `operation_type` varchar(64) DEFAULT NULL,
  `operator` varchar(64) DEFAULT NULL,
  `target_type` varchar(64) DEFAULT NULL,
  `target_name` varchar(64) DEFAULT NULL,
  `target_id` varchar(64) DEFAULT NULL,
  `target_detail` text,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dns_operation_log`
--

LOCK TABLES `dns_operation_log` WRITE;
/*!40000 ALTER TABLE `dns_operation_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `dns_operation_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dns_record`
--

DROP TABLE IF EXISTS `dns_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dns_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(64) DEFAULT NULL,
  `record_type` varchar(64) DEFAULT NULL,
  `ttl` varchar(64) DEFAULT NULL,
  `value` varchar(64) DEFAULT NULL,
  `view_name` varchar(64) DEFAULT NULL,
  `comment` varchar(64) DEFAULT NULL,
  `creator` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `enabled` varchar(64) DEFAULT NULL,
  `alive` varchar(64) DEFAULT NULL,
  `outter_record_id` varchar(64) DEFAULT NULL,
  `zone_id` int(11) DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_record_host` (`host`),
  KEY `ix_dns_record_zone_id` (`zone_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dns_record`
--

LOCK TABLES `dns_record` WRITE;
/*!40000 ALTER TABLE `dns_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `dns_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dns_server`
--

DROP TABLE IF EXISTS `dns_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dns_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(64) DEFAULT NULL,
  `ip` varchar(64) DEFAULT NULL,
  `env` varchar(64) DEFAULT NULL,
  `dns_server_type` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `zb_process_itemid` varchar(64) DEFAULT NULL,
  `zb_port_itemid` varchar(64) DEFAULT NULL,
  `zb_resolve_itemid` varchar(64) DEFAULT NULL,
  `zb_resolve_rate_itemid` varchar(64) DEFAULT NULL,
  `server_log` text,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_server_host` (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dns_server`
--

LOCK TABLES `dns_server` WRITE;
/*!40000 ALTER TABLE `dns_server` DISABLE KEYS */;
/*!40000 ALTER TABLE `dns_server` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dns_view`
--

DROP TABLE IF EXISTS `dns_view`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dns_view` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `acl` text,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_view_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dns_view`
--

LOCK TABLES `dns_view` WRITE;
/*!40000 ALTER TABLE `dns_view` DISABLE KEYS */;
/*!40000 ALTER TABLE `dns_view` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dns_view_zone`
--

DROP TABLE IF EXISTS `dns_view_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dns_view_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `view_id` int(11) DEFAULT NULL,
  `zone_id` int(11) DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_view_zone_view_id` (`view_id`),
  KEY `ix_dns_view_zone_zone_id` (`zone_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dns_view_zone`
--

LOCK TABLES `dns_view_zone` WRITE;
/*!40000 ALTER TABLE `dns_view_zone` DISABLE KEYS */;
/*!40000 ALTER TABLE `dns_view_zone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dns_zone`
--

DROP TABLE IF EXISTS `dns_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dns_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `zone_group` int(11) DEFAULT NULL,
  `zone_type` varchar(64) DEFAULT NULL,
  `forwarders` varchar(64) DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_zone_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dns_zone`
--

LOCK TABLES `dns_zone` WRITE;
/*!40000 ALTER TABLE `dns_zone` DISABLE KEYS */;
/*!40000 ALTER TABLE `dns_zone` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-12-05 16:06:27
