SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


;
;
;
;

CREATE TABLE `BankAccounts` (
  `AccountID` int(11) NOT NULL,
  `AccountNumber` varchar(50) DEFAULT NULL,
  `BankName` varchar(100) DEFAULT NULL,
  `Currency` varchar(3) DEFAULT NULL,
  `Balance` decimal(15,2) DEFAULT NULL,
  `AccountType` varchar(20) DEFAULT NULL,
  `SellerID` int(11) DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `BankTransactions` (
  `TransactionID` int(11) NOT NULL,
  `AccountID` int(11) DEFAULT NULL,
  `TransactionDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `DateID` int(11) DEFAULT NULL,
  `Amount` decimal(15,2) DEFAULT NULL,
  `TransactionType` varchar(20) DEFAULT NULL,
  `Description` varchar(200) DEFAULT NULL,
  `Counterparty` varchar(100) DEFAULT NULL,
  `ReferenceNumber` varchar(50) DEFAULT NULL,
  `SellerID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Categories` (
  `CategoryID` int(11) NOT NULL,
  `CategoryName` varchar(50) DEFAULT NULL,
  `ParentCategoryID` int(11) DEFAULT NULL,
  `Description` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Countries` (
  `CountryID` int(11) NOT NULL,
  `CountryName` varchar(50) DEFAULT NULL,
  `Continent` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Customers` (
  `CustomerID` int(11) NOT NULL,
  `FirstName` varchar(50) DEFAULT NULL,
  `LastName` varchar(50) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `Address` varchar(200) DEFAULT NULL,
  `CountryID` int(11) DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `DateDimension` (
  `DateID` int(11) NOT NULL,
  `FullDate` date DEFAULT NULL,
  `Year` int(11) DEFAULT NULL,
  `Quarter` int(11) DEFAULT NULL,
  `Month` int(11) DEFAULT NULL,
  `MonthName` varchar(20) DEFAULT NULL,
  `Day` int(11) DEFAULT NULL,
  `DayOfWeek` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `OrderDetails` (
  `OrderDetailID` int(11) NOT NULL,
  `OrderID` int(11) DEFAULT NULL,
  `ProductID` int(11) DEFAULT NULL,
  `Quantity` int(11) DEFAULT NULL,
  `UnitPrice` decimal(10,2) DEFAULT NULL,
  `UnitCostPrice` decimal(10,2) DEFAULT NULL,
  `Discount` decimal(5,2) DEFAULT '0.00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Orders` (
  `OrderID` int(11) NOT NULL,
  `CustomerID` int(11) DEFAULT NULL,
  `SellerID` int(11) DEFAULT NULL,
  `OrderDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `DateID` int(11) DEFAULT NULL,
  `TotalAmount` decimal(10,2) DEFAULT NULL,
  `Status` varchar(20) DEFAULT NULL,
  `ShippingAddress` varchar(200) DEFAULT NULL,
  `CountryID` int(11) DEFAULT NULL,
  `PaymentMethod` varchar(50) DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Products` (
  `ProductID` int(11) NOT NULL,
  `ProductName` varchar(100) DEFAULT NULL,
  `CategoryID` int(11) DEFAULT NULL,
  `SellerID` int(11) DEFAULT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `CostPrice` decimal(10,2) DEFAULT NULL,
  `StockQuantity` int(11) DEFAULT NULL,
  `Description` varchar(500) DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Promotions` (
  `PromotionID` int(11) NOT NULL,
  `PromotionName` varchar(100) DEFAULT NULL,
  `StartDateID` int(11) DEFAULT NULL,
  `EndDateID` int(11) DEFAULT NULL,
  `DiscountPercentage` decimal(5,2) DEFAULT NULL,
  `ProductID` int(11) DEFAULT NULL,
  `CategoryID` int(11) DEFAULT NULL,
  `SellerID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Regions` (
  `RegionID` int(11) NOT NULL,
  `RegionName` varchar(50) DEFAULT NULL,
  `CountryID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Sellers` (
  `SellerID` int(11) NOT NULL,
  `FirstName` varchar(50) DEFAULT NULL,
  `LastName` varchar(50) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `SellerType` varchar(20) DEFAULT NULL,
  `RegionID` int(11) DEFAULT NULL,
  `HireDate` datetime DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `BankAccounts`
  ADD PRIMARY KEY (`AccountID`),
  ADD UNIQUE KEY `AccountNumber` (`AccountNumber`),
  ADD KEY `SellerID` (`SellerID`);

ALTER TABLE `BankTransactions`
  ADD PRIMARY KEY (`TransactionID`),
  ADD KEY `AccountID` (`AccountID`),
  ADD KEY `DateID` (`DateID`),
  ADD KEY `SellerID` (`SellerID`);

ALTER TABLE `Categories`
  ADD PRIMARY KEY (`CategoryID`),
  ADD KEY `ParentCategoryID` (`ParentCategoryID`);

ALTER TABLE `Countries`
  ADD PRIMARY KEY (`CountryID`);

ALTER TABLE `Customers`
  ADD PRIMARY KEY (`CustomerID`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD KEY `CountryID` (`CountryID`);

ALTER TABLE `DateDimension`
  ADD PRIMARY KEY (`DateID`);

ALTER TABLE `OrderDetails`
  ADD PRIMARY KEY (`OrderDetailID`),
  ADD KEY `OrderID` (`OrderID`),
  ADD KEY `ProductID` (`ProductID`);

ALTER TABLE `Orders`
  ADD PRIMARY KEY (`OrderID`),
  ADD KEY `CustomerID` (`CustomerID`),
  ADD KEY `SellerID` (`SellerID`),
  ADD KEY `DateID` (`DateID`),
  ADD KEY `CountryID` (`CountryID`);

ALTER TABLE `Products`
  ADD PRIMARY KEY (`ProductID`),
  ADD KEY `CategoryID` (`CategoryID`),
  ADD KEY `SellerID` (`SellerID`);

ALTER TABLE `Promotions`
  ADD PRIMARY KEY (`PromotionID`),
  ADD KEY `StartDateID` (`StartDateID`),
  ADD KEY `EndDateID` (`EndDateID`),
  ADD KEY `ProductID` (`ProductID`),
  ADD KEY `CategoryID` (`CategoryID`),
  ADD KEY `SellerID` (`SellerID`);

ALTER TABLE `Regions`
  ADD PRIMARY KEY (`RegionID`),
  ADD KEY `CountryID` (`CountryID`);

ALTER TABLE `Sellers`
  ADD PRIMARY KEY (`SellerID`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD KEY `RegionID` (`RegionID`);

ALTER TABLE `BankAccounts`
  MODIFY `AccountID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `BankTransactions`
  MODIFY `TransactionID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Categories`
  MODIFY `CategoryID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Countries`
  MODIFY `CountryID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Customers`
  MODIFY `CustomerID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `DateDimension`
  MODIFY `DateID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `OrderDetails`
  MODIFY `OrderDetailID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Orders`
  MODIFY `OrderID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Products`
  MODIFY `ProductID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Promotions`
  MODIFY `PromotionID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Regions`
  MODIFY `RegionID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Sellers`
  MODIFY `SellerID` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `BankAccounts`
  ADD CONSTRAINT `bankaccounts_ibfk_1` FOREIGN KEY (`SellerID`) REFERENCES `Sellers` (`SellerID`);

ALTER TABLE `BankTransactions`
  ADD CONSTRAINT `banktransactions_ibfk_1` FOREIGN KEY (`AccountID`) REFERENCES `BankAccounts` (`AccountID`),
  ADD CONSTRAINT `banktransactions_ibfk_2` FOREIGN KEY (`DateID`) REFERENCES `DateDimension` (`DateID`),
  ADD CONSTRAINT `banktransactions_ibfk_3` FOREIGN KEY (`SellerID`) REFERENCES `Sellers` (`SellerID`);

ALTER TABLE `Categories`
  ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`ParentCategoryID`) REFERENCES `Categories` (`CategoryID`);

ALTER TABLE `Customers`
  ADD CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`CountryID`) REFERENCES `Countries` (`CountryID`);

ALTER TABLE `OrderDetails`
  ADD CONSTRAINT `orderdetails_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `Orders` (`OrderID`),
  ADD CONSTRAINT `orderdetails_ibfk_2` FOREIGN KEY (`ProductID`) REFERENCES `Products` (`ProductID`);

ALTER TABLE `Orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`CustomerID`) REFERENCES `Customers` (`CustomerID`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`SellerID`) REFERENCES `Sellers` (`SellerID`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`DateID`) REFERENCES `DateDimension` (`DateID`),
  ADD CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`CountryID`) REFERENCES `Countries` (`CountryID`);

ALTER TABLE `Products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`CategoryID`) REFERENCES `Categories` (`CategoryID`),
  ADD CONSTRAINT `products_ibfk_2` FOREIGN KEY (`SellerID`) REFERENCES `Sellers` (`SellerID`);

ALTER TABLE `Promotions`
  ADD CONSTRAINT `promotions_ibfk_1` FOREIGN KEY (`StartDateID`) REFERENCES `DateDimension` (`DateID`),
  ADD CONSTRAINT `promotions_ibfk_2` FOREIGN KEY (`EndDateID`) REFERENCES `DateDimension` (`DateID`),
  ADD CONSTRAINT `promotions_ibfk_3` FOREIGN KEY (`ProductID`) REFERENCES `Products` (`ProductID`),
  ADD CONSTRAINT `promotions_ibfk_4` FOREIGN KEY (`CategoryID`) REFERENCES `Categories` (`CategoryID`),
  ADD CONSTRAINT `promotions_ibfk_5` FOREIGN KEY (`SellerID`) REFERENCES `Sellers` (`SellerID`);

ALTER TABLE `Regions`
  ADD CONSTRAINT `regions_ibfk_1` FOREIGN KEY (`CountryID`) REFERENCES `Countries` (`CountryID`);

ALTER TABLE `Sellers`
  ADD CONSTRAINT `sellers_ibfk_1` FOREIGN KEY (`RegionID`) REFERENCES `Regions` (`RegionID`);
COMMIT;

;
;
;
