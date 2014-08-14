setwd("/Users/Sammy/Dropbox/project/graphs/sam")
install.packages("jsonlite")
install.packages("glmnet")
library(jsonlite)
library(glmnet)
library(plyr)
library(ggplot2)
library(reshape2)


#import all the data into one big dataframe
totaldata <- fromJSON("/Users/Sammy/Dropbox/project/code/clean_data/oldfeatures/featurized1.json")
totaldata$userscore <- NULL

mean(abs(totaldata$revenue-mean(totaldata$revenue)))



View(totaldata)

## baseline
# summary(glm(revenue ~ budget + runtime + G + PG + PG_13 + R + 
#       Action + Adventure + Animation + Biography + Comedy + Crime + Drama + 
#       Family + Fantasy + History + Horror + Music + Musical + Mystery + 
#       Romance + SciFi + Short + Sport + Thriller + War + Western + 
#       January + February + March + April + May + June + July + August + September + October + November + December, 
#     data=totaldata,family=gaussian(link="log")))

## divide into training and testing
# chronologically (first 2894)
train1data <- subset(totaldata,totaldata[,"year"]<2009)
test1data <- subset(totaldata,totaldata[,"year"]>=2009)

# randomly, 2894 for training
set.seed(1000)
rands <- sample(3697,2894)
train2data <- totaldata[rands,]
test2data <- totaldata[-rands,]
mean(abs(test2data$revenue-mean(train2data$revenue)))



## use training data to fit model, first training set first
glm.1 <- glm(revenue ~ budget + runtime + G + PG + PG_13 + R + 
               Action + Adventure + Animation + Biography + Comedy + Crime + Drama + 
               Family + Fantasy + History + Horror + Music + Musical + Mystery + 
               Romance + SciFi + Short + Sport + Thriller + War + Western + 
               January + February + March + April + May + June + July + August + September + October + November + December, 
             data=train1data,family=gaussian)
glm.train.1 <- mean(abs(predict(glm.1,train1data) - train1data$revenue))
glm.train.1
glm.test.1 <- mean(abs(predict(glm.1,test1data) - test1data$revenue))
glm.test.1

## lasso and ridge
glmnet.mean.l1.error <- function(model, x, y) {
  preds <- predict(model, x, type="response")
  aaply(preds, 2, function (yhat) mean(abs(y - yhat)))
}

# compute the ridge path
train.x <- as.matrix(train1data[,c(1:29,31:39,52)],header=T)
train.y <- train1data[,51]
test.x <- as.matrix(test1data[,c(1:29,31:39,52)],header=T)
test.y <- test1data[,51]
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0)
# plot the ridge path
plot(ridge.model)
dev.copy(png,'ridgecoef1.png')
dev.off()
# the action is in lambda \in (0,1)
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0,lambda=seq(0,1, by=0.001))
ridge.model
# compute training error
ridge.train <- glmnet.mean.l1.error(ridge.model, train.x, train.y)
# plot training error as a function of complexity
qplot(ridge.model$lambda, ridge.train, geom="line")
min(ridge.train)
# get the test error and make the same plot
ridge.test <- glmnet.mean.l1.error(ridge.model, test.x, test.y)
qplot(ridge.model$lambda, ridge.test, geom="line")
min(ridge.test)
# lasso
lasso.model <- glmnet(train.x, train.y, family = "gaussian", alpha = 1)
lasso.model$beta
plot(lasso.model)
dev.copy(png,'lassocoef1.png')
dev.off()
lasso.train <- glmnet.mean.l1.error(lasso.model, train.x, train.y)
qplot(lasso.model$lambda, lasso.train, geom="line")
min(lasso.train)
lasso.test <- glmnet.mean.l1.error(lasso.model, test.x, test.y)
qplot(lasso.model$lambda, lasso.test, geom="line")
min(lasso.test)

qplot(ridge.model$lambda, ridge.train, geom="line")
dev.copy(png,'ridgetrain1.png')
dev.off()
qplot(ridge.model$lambda, ridge.test, geom="line")
dev.copy(png,'ridgetest1.png')
dev.off()
qplot(lasso.model$lambda, lasso.train, geom="line")
dev.copy(png,'lassotrain1.png')
dev.off()
qplot(lasso.model$lambda, lasso.test, geom="line")
dev.copy(png,'lassotest1.png')
dev.off()

## random train/test
glm.2 <- glm(revenue ~ budget + runtime + G + PG + PG_13 + R + 
               Action + Adventure + Animation + Biography + Comedy + Crime + Drama + 
               Family + Fantasy + History + Horror + Music + Musical + Mystery + 
               Romance + SciFi + Short + Sport + Thriller + War + Western + 
               January + February + March + April + May + June + July + August + September + October + November + December, 
             data=train2data,family=gaussian)
glm.train.2 <- mean(abs(predict(glm.2,train2data) - train2data$revenue))
glm.train.2
glm.test.2 <- mean(abs(predict(glm.2,test2data) - test2data$revenue))
glm.test.2
## lasso and ridge
# compute the ridge path
train.x <- as.matrix(train2data[,c(1:29,31:39,52)],header=T)
train.y <- train2data[,51]
test.x <- as.matrix(test2data[,c(1:29,31:39,52)],header=T)
test.y <- test2data[,51]
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0)
# plot the ridge path
plot(ridge.model)
dev.copy(png,'ridgecoef2.png')
dev.off()
# the action is in lambda \in (0,1)
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0,lambda=seq(0,1, by=0.001))
ridge.model
# compute training error
ridge.train <- glmnet.mean.l1.error(ridge.model, train.x, train.y)
# plot training error as a function of complexity
qplot(ridge.model$lambda, ridge.train, geom="line")
min(ridge.train)
# get the test error and make the same plot
# q: why does the plot look like this?
ridge.test <- glmnet.mean.l1.error(ridge.model, test.x, test.y)
qplot(ridge.model$lambda, ridge.test, geom="line")
min(ridge.test)
# lasso 
lasso.model <- glmnet(train.x, train.y, family = "gaussian", alpha = 1)
lasso.model$beta
plot(lasso.model)
dev.copy(png,'lassocoef2.png')
dev.off()
lasso.train <- glmnet.mean.l1.error(lasso.model, train.x, train.y)
qplot(lasso.model$lambda, lasso.train, geom="line")
min(lasso.train)
lasso.test <- glmnet.mean.l1.error(lasso.model, test.x, test.y)
qplot(lasso.model$lambda, lasso.test, geom="line")
min(lasso.test)

qplot(ridge.model$lambda, ridge.train, geom="line")
dev.copy(png,'ridgetrain2.png')
dev.off()
qplot(ridge.model$lambda, ridge.test, geom="line")
dev.copy(png,'ridgetest2.png')
dev.off()
qplot(lasso.model$lambda, lasso.train, geom="line")
dev.copy(png,'lassotrain2.png')
dev.off()
qplot(lasso.model$lambda, lasso.test, geom="line")
dev.copy(png,'lassotest2.png')
dev.off()

######## GAMMA STUFF ########
glm.3 <- glm(revenue ~ budget + runtime + G + PG + PG_13 + R + 
               Action + Adventure + Animation + Biography + Comedy + Crime + Drama + 
               Family + Fantasy + History + Horror + Music + Musical + Mystery + 
               Romance + SciFi + Short + Sport + Thriller + War + Western + 
               January + February + March + April + May + June + July + August + September + October + November + December, 
             data=train1data,family=Gamma(link='identity'),start=coefs)
coefs <- coef(glm.3)
glm.train.3 <- mean(abs(predict(glm.3,train1data) - train1data$revenue))
predict(glm.3,train1data) - train1data
glm.train.3
glm.test.3 <- mean(abs(predict(glm.3,test1data) - test1data$revenue))
glm.test.3
## lasso and ridge
# compute the ridge path
train.x <- as.matrix(train1data[,c(1:38,51)],header=T)
train.y <- train1data[,50]
test.x <- as.matrix(test1data[,c(1:38,51)],header=T)
test.y <- test1data[,50]
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0)
# plot the ridge path
plot(ridge.model)
# the action is in lambda \in (0,1)
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0,lambda=seq(0,1, by=0.001))
ridge.model
# compute training error
ridge.train <- glmnet.mean.l1.error(ridge.model, train.x, train.y)
# plot training error as a function of complexity
qplot(ridge.model$lambda, ridge.train, geom="line")
which.min(ridge.train)
# get the test error and make the same plot
ridge.test <- glmnet.mean.l1.error(ridge.model, test.x, test.y)
qplot(ridge.model$lambda, ridge.test, geom="line")
which.min(ridge.test)
# lasso
lasso.model <- glmnet(train.x, train.y, family = "gaussian", alpha = 1)
lasso.model$beta
plot(lasso.model)
lasso.train <- glmnet.mean.l1.error(lasso.model, train.x, train.y)
qplot(lasso.model$lambda, lasso.train, geom="line")
min(lasso.train)
lasso.test <- glmnet.mean.l1.error(lasso.model, test.x, test.y)
qplot(lasso.model$lambda, lasso.test, geom="line")
min(lasso.test)

######################### WITH ACTORS AND WHATNOT #########################
train <- fromJSON("/Users/Sammy/Dropbox/project/code/clean_data/featurized2_train.json")
test <- fromJSON("/Users/Sammy/Dropbox/project/code/clean_data/featurized2_test.json")
glm.1 <- glm(revenue ~ budget + runtime + G + PG + PG_13 + R + 
               Action + Adventure + Animation + Biography + Comedy + Crime + Drama + 
               Family + Fantasy + History + Horror + Music + Musical + Mystery + 
               Romance + SciFi + Short + Sport + Thriller + War + Western + 
               January + February + March + April + May + June + July + August + September + October + November + December + 
               actor0 + actor1 + actor2 + directors + writers + production, 
             data=train,family=gaussian)
glm.train.1 <- mean(abs(predict(glm.1,train) - train$revenue))
glm.train.1
glm.test.1 <- mean(abs(predict(glm.1,test) - test$revenue))
glm.test.1
## lasso and ridge
# compute the ridge path
train.x <- as.matrix(train[,c(1:29,31:43,46,48,49)],header=T)
train.y <- train[,47]
test.x <- as.matrix(test[,c(1:29,31:43,46,48,49)],header=T)
test.y <- test[,47]
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0)
# plot the ridge path
plot(ridge.model)
dev.copy(png,'ridgecoef3.png')
dev.off()
# the action is in lambda \in (0,1)
ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0,lambda=seq(0,1, by=0.001))
ridge.model
# compute training error
ridge.train <- glmnet.mean.l1.error(ridge.model, train.x, train.y)
# plot training error as a function of complexity
qplot(ridge.model$lambda, ridge.train, geom="line")
dev.copy(png,'ridgetrain3.png')
dev.off()
min(ridge.train)
# get the test error and make the same plot
ridge.test <- glmnet.mean.l1.error(ridge.model, test.x, test.y)
qplot(ridge.model$lambda, ridge.test, geom="line")
dev.copy(png,'ridgetest3.png')
dev.off()
min(ridge.test)
# lasso
lasso.model <- glmnet(train.x, train.y, family = "gaussian", alpha = 1)
#lasso.model$beta
plot(lasso.model)
dev.copy(png,'lassocoef3.png')
dev.off()
lasso.train <- glmnet.mean.l1.error(lasso.model, train.x, train.y)
qplot(lasso.model$lambda, lasso.train, geom="line")
dev.copy(png,'lassotrain3.png')
dev.off()
min(lasso.train)
lasso.test <- glmnet.mean.l1.error(lasso.model, test.x, test.y)
qplot(lasso.model$lambda, lasso.test, geom="line")
dev.copy(png,'ridgetest3.png')
dev.off()
min(lasso.test)



