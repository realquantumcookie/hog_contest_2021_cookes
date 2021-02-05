"""
    This file contains your final_strategy that will be submitted to the contest.
    It will only be run on your local machine, so you can import whatever you want!
    Remember to supply a unique PLAYER_NAME or your submission will not succeed.
"""
import gamecalc
import dice as diceLib


PLAYER_NAME = 'QuantumCookie01'  # Change this line!

def getWinningChance(currentPlayerLastTimeTrot, opponentLastTimeTrot, numToRoll, selfScore, opponentScore, targetScore, turnNum = 0, currentPlayer = 0):
    def getWinningChanceForSpecificScoreIncrease(moreTurn, usedTimeTrot, opponentLastTimeTrot, newScore, oldScore, opponentScore, targetScore, turnNum = 0):
        if(newScore >= targetScore):
            return 1.0

        sumChance = 0.0
        numChance = 10
        if moreTurn:
            for i in range(0,numChance+1):
                sumChance += getWinningChance(usedTimeTrot,opponentLastTimeTrot,i,newScore,opponentScore,targetScore,turnNum+1,0)
        else:
            for i in range(0,numChance+1):
                sumChance += 1.0 - getWinningChance(opponentLastTimeTrot,usedTimeTrot,i,opponentScore,newScore,targetScore,0,0)
        chance = sumChance / numChance
        getWinningChance.result_dict[currentKey] = chance
        return chance
    
    def winningChanceForDicePossibility(currentLastTimeTrot, opponentLastTimeTrot, currentScore, opponentScore, numDice, targetScore, turnNum = 0, previousNums = []):
        diceSideNum = 6 if turnNum == 0 else 8
        if(numDice >= 1):
            currentNums = previousNums
            lastIndex = len(currentNums)
            chanceSum = 0.0
            chanceTotal = diceSideNum
            for i in range(1,diceSideNum+1):
                if(len(currentNums) == lastIndex):
                    currentNums.append(i)
                else:
                    currentNums[lastIndex] = i
                
                chanceSum += winningChanceForDicePossibility(currentLastTimeTrot, opponentLastTimeTrot,currentScore,opponentScore,numDice-1,targetScore,turnNum,currentNums)      
            
            return chanceSum / chanceTotal
        else:
            scoreIncrease = gamecalc.calc_turn_score(previousNums,opponentScore)
            newScore = currentScore + scoreIncrease
            moreBoar = gamecalc.more_boar(newScore,opponentScore)
            timeTrot = gamecalc.time_trot(turnNum,len(previousNums),currentLastTimeTrot)
            moreTurn = moreBoar or timeTrot
            return getWinningChanceForSpecificScoreIncrease(moreTurn,timeTrot, opponentLastTimeTrot,newScore,currentScore,opponentScore,targetScore,turnNum)


    
    currentKey = (currentPlayerLastTimeTrot,opponentLastTimeTrot,numToRoll,selfScore,opponentScore,targetScore,turnNum > 0,currentPlayer)
    if currentKey in getWinningChance.result_dict:
        return getWinningChance.result_dict[currentKey]
    if not(currentPlayer == 0):
        return 1.0 - getWinningChance(opponentLastTimeTrot,currentPlayerLastTimeTrot,numToRoll,opponentScore,selfScore,targetScore,turnNum,0)
    
    dice = getWinningChance.dice_six if turnNum == 0 else getWinningChance.dice_eight
    
    return winningChanceForDicePossibility(currentPlayerLastTimeTrot,opponentLastTimeTrot,selfScore,opponentScore,numToRoll,targetScore,turnNum)

getWinningChance.dice_eight = diceLib.make_fair_dice(8)
getWinningChance.dice_six = diceLib.make_fair_dice(6)
getWinningChance.result_dict = {}

def strategy_to_play(turnNum, dice_side_num, selfScore, opponentScore, canTimeTrot):
    """This is the function to implement final strategy, it gives you all possible informations about the current turn
    turnNum = number of consecutive turn the player is playing, starting from 0
    canTimeTrot = if the player can use the time trot strategy in this turn

    returns numToRoll
    """
    winningChances = []
    biggestWinningRate = 0
    biggestWinningIndex = 0

    targetScore = 100

    while (selfScore > targetScore or opponentScore > targetScore):
        targetScore *= 2

    for i in range(0,11):
        currentWinningRate = getWinningChance(not(canTimeTrot),False,i,selfScore,opponentScore,targetScore,turnNum,0)
        winningChances.append(currentWinningRate)
        if(currentWinningRate > biggestWinningRate):
            biggestWinningRate = currentWinningRate
            biggestWinningIndex = i
    return biggestWinningIndex
    



def final_strategy(score, opponent_score):
    turnNumber = 0
    canTrot = False
    diceSideNum = 6

    #determine if this is the first turn or not
    if(final_strategy.last_opponent_score < opponent_score):
        turnNumber = 0
        diceSideNum = 6
        canTrot = True
    else:
        turnNumber = final_strategy.last_turn_num + 1
        canTrot = not(final_strategy.last_time_trot)
        #we should see whether last time really used the "time trot strategy because it might have triggered a more boar"
        if gamecalc.more_boar(score,opponent_score):
            canTrot = True
        diceSideNum = 8

    #determine strategy to play
    strategyReturn = strategy_to_play(turnNumber,diceSideNum,score,opponent_score,canTrot)
    
    #decode strategyReturn
    numToRollDice = strategyReturn
    isTimeTrot = gamecalc.time_trot(turnNumber,numToRollDice,not(canTrot))

    #update state variables
    final_strategy.last_opponent_score = opponent_score
    final_strategy.last_turn_num = turnNumber
    final_strategy.last_self_score = score
    final_strategy.last_time_trot = isTimeTrot

    return numToRollDice

#In the global frame we want to initialize 
final_strategy.last_opponent_score = -1
final_strategy.last_turn_num = 0
final_strategy.last_self_score = 0
final_strategy.last_time_trot = False