# Strict Mode
***
# Description
> The default behaviour is that a user is kicked out of the server if he didn't meet his red card.
> 
> Strict mode allows a user to have a choice about this matter; if the mode is disabled then the user won't be kicked out of the server even if they didn't meet their red card.
> 
> Instead, they will be banned from the bot until further notice but they will still be on server.

### Default behaviour: ON (Users are kicked out of server if they didn't meet their red card)

***
# Commands and Consequences
> On Event: Registering
> 
> Give Choice to have the mode on or off, default is ON

> On Event: Red card not met
> 
> If mode is on: kick user out of server
> 
> If mode is off: ban user from bot but don't kick them out.

> Command: /strictmode < text >
> 
> Text can either be "on" or "off".
> 
> Can only be used by an ADMIN