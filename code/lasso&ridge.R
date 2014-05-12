library(glmnet)
library(plyr)
library(ggplot2)
library(reshape2)

#Read in Dataset
dat <- read.csv("./Desktop/COS424/Assignment4/Data.csv", header = T)

#set up training set and test set
train <- dat[!dat$Test,]
test  <-  dat[dat$Test,]

#glmnet needs things in this form
train.x <- as.matrix(train[,3:11], header = T)
train.y <- train[,2]
test.x <- as.matrix(test[,3:11], header = T)
test.y <- test[,2]

  mle.model <- lm(train.y ~ train.x, data=train)
  summary(mle.model)

  # compute training error
  mle.train <- mean(abs(predict(mle.model, train) - train.y))
  mle.train

  mle.test <- mean(abs(predict(mle.model, test) - test.y))
  mle.test
  
  
  
  glmnet.mean.l1.error <- function(model, x, y)
{
  preds <- predict(model, x, type="response")
  aaply(preds, 2, function (yhat) mean(abs(y - yhat)))
}

  # compute the ridge path
  ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0)

  # plot the ridge path
  plot(ridge.model)

  # the action is in lambda \in (0,1)
  ridge.model <- glmnet(train.x, train.y, family="gaussian", alpha=0,lambda=seq(0,1, by=0.001))
  ridge.model


  # compute training error
  ridge.train <- glmnet.mean.l1.error(ridge.model, train.x, train.y)
  
    # plot training error as a function of complexity
  # q: what do you expect?
  # q: why does the plot look like this?
  qplot(ridge.model$lambda, ridge.train, geom="line")

  # get the test error and make the same plot
  # q: why does the plot look like this?
  ridge.test <- glmnet.mean.l1.error(ridge.model, test.x, test.y)
  qplot(ridge.model$lambda, ridge.test, geom="line")
  
 #### LASSO ##### 
  
  lasso.model <- glmnet(train.x, train.y, family = "gaussian", alpha = 1)
                                  lasso.model$beta
  plot(lasso.model)
  lasso.train <- glmnet.mean.l1.error(lasso.model, train.x, train.y)
  qplot(lasso.model$lambda, lasso.train, geom="line")

  lasso.test <- glmnet.mean.l1.error(lasso.model, test.x, test.y)
  qplot(lasso.model$lambda, lasso.test, geom="line")



