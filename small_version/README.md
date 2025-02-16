Small Command Line version of Pokemon game to help determine organization/models.

Known Bugs/what to fix/implement next:
    1. documentation
    2. testing
    3. better feedback/error messages on user input
    4. game makes you select active when game is over
    5. state winner at the end
    6. sort hand/bench

Stuff to do:
    0. server/client programs to allow multiplayer
    1. abilities
    2. conditions
    2. more cards
    3. deck building
    4. card collecting
    5. battle building
    6. energy cards
    7. alternative evolution/rule options
    8. visualizations
    9. sabrina to multiple effects
    10. EnergyContainer/Collection to mutable objects

Test next:
    1. retreat

Potential issues:
    1. Successful attack/ability with effect that fails: return False instead of true
    2. Effect with multiple user inputs: 
    3. Action queues action with same name: would be removed from queue
    4. Action with user inputs: maybe?