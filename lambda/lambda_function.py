# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

difficulty_drinks = ["For Difficulty easy we can offer you following drinks: Beer and Wine.",
                        "For Difficulty intermediate we can offer you following drinks: Berliner Luft shot or Mexikaner.",
                            "For Difficulty hard we can offer you following drinks: Vodka Bull or Whiskey."]


trueOrfalse = ["Keine Fragen mehr verfügbar!",
                "Electrons move faster than the speed of light.", "False",
                "The Mona Liza was stolen from the Louvre in 1911.", "True",
                "There is no snow on Minecraft.", "False",
                "Light travels in a straight line.", "True",
                "Emus can’t fly.", "True"]

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to DrinkingGames! Who is playing tonight ?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class PlayerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PlayerIntent")(handler_input)

    def handle(self, handler_input):
        
        #list of player names
        slots = handler_input.request_envelope.request.intent.slots
        playerNames = slots["names"].value
        playerNamesList = playerNames.split(" ")
        
        #highscore list
        length = len(playerNamesList)
        highScore = [0]
        while(length > 1):
            highScore.append(0)
            length -= 1
        
        atr = handler_input.attributes_manager.session_attributes
        atr["playerNamesList"] = playerNamesList
        atr["highscore"] = highScore
        
        speak_output = "Nice to have you here! So how long and on which difficulty do you want to play ?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GameIntent")(handler_input)

    def handle(self, handler_input):
        
        #session attributes
        atr = handler_input.attributes_manager.session_attributes
        #slot
        slots = handler_input.request_envelope.request.intent.slots
        
        drink = slots["difficulty"].value
        rounds = slots["time"].value
        
        atr["rounds"] = rounds
        atr["usedNumbers"] = [0]
        
        #output which drink is recommended
        if drink == "easy":
            speak_output = difficulty_drinks[0]
        elif drink == "intermediate":
            speak_output = difficulty_drinks[1]
        else:
            speak_output = difficulty_drinks[2]
        
        speak_output = speak_output + " So are you guys ready to play?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class PlayingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PlayingIntent")(handler_input)

    def handle(self, handler_input):
        atr = handler_input.attributes_manager.session_attributes
        
        #round
        game_round = atr["rounds"]
        game_round = int(game_round)
        
        #Used Questions
        used_numbers = atr["usedNumbers"]
        
        #listen length
        length = len(trueOrfalse)
        
        if(game_round > 0):
            #random number
            randInt = random.randrange(length)
            
            #checking if random number is already used
            while((randInt%2 == 0) or (randInt in used_numbers)):
                randInt = random.randrange(length)
                
            #save used number, so questions won't repeat
            used_numbers.append(randInt)
            atr["usedNumbers"] = used_numbers
            
            #decrease rounds
            game_round -= 1
            atr["rounds"] = game_round
            
            #picks random player to answer question
            playerName = atr["playerNamesList"]
            playerLength = len(playerName)
            randomInt = random.randrange(playerLength)
            #for highscore
            atr["randomInt"] = randomInt
            playerNameGuess = playerName[randomInt].lower()
            
            speak_output = playerNameGuess + " this one is for you. " + trueOrfalse[randInt] + " Is it true or false ?"
        
        #end of game, no rounds left
        else:
            speak_output = "Game Over"
            return (
            handler_input.response_builder
                .speak(speak_output)
                .response
            )
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CorrectionIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CorrectionIntent")(handler_input)
    
    def handle(self, handler_input):
        #user input
        eingabe = handler_input.request_envelope.request.intent.slots['userInput'].value
        eingabe = eingabe.lower()
        
        #gamerounds
        atr = handler_input.attributes_manager.session_attributes
        game_round = atr["rounds"]
        game_round = int(game_round)
        
        #randomInt indize for player
        randomInt = atr["randomInt"]
        randomInt = int(randomInt)
        
        #highscore list
        highscore = atr["highscore"]
        
        #list of used numbers
        used_numbers = atr["usedNumbers"]
        
        #finding right answer
        intAnswer = used_numbers[-1] + 1
        right_answer = trueOrfalse[intAnswer]
        
        #player names
        playerNames = atr["playerNamesList"]
        lengthPlayerNames = len(playerNames)
        
        #checking if user input is correct 
        if((eingabe == right_answer) or (eingabe == right_answer.lower())):
            #points for right answer for player
            highscore[randomInt] += 100
            atr["highscore"] = highscore
            speak_output = "That's correct! 100 points for you " + playerNames[randomInt] + "."
        else:
            #points for right answer for player
            highscore[randomInt] -= 50
            atr["highscore"] = highscore
            speak_output = "That's not correct! -50 points for " + playerNames[randomInt] + "."
        
        if(game_round != 0):
            speak_output += " Guys Are you ready for the next question?"
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        
        #output highscore
        points = atr["highscore"]
        index = 0
        highscoreResult = "The results are "
        
        #gives out every players points
        while(index < lengthPlayerNames):
            highscoreResult += playerNames[index] + " has " + str(points[index]) + " points. "
            index += 1
        
        speak_output += " That was your last question. " + highscoreResult + "We hope you liked our Drinking Game! And have fun partying!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PlayerIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(CorrectionIntentHandler())
sb.add_request_handler(GameIntentHandler())
sb.add_request_handler(PlayingIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()