

class Model:
    OPERATORS = ['/', '*', '-', '+']
    def __init__(self):
        self.value      = '0'
        self.prev_value = ''
        self.operator   = ''
        self.clear_value_next = True
        self.last_pressed = ''

    def calculate(self, caption):
        if self.clear_value_next == True:
            # In some cases we don't want to reset the value, but just change the flag
            if (self.last_pressed == "=" and caption == "=") or caption in self.OPERATORS:
                pass
            # Dont allow +/- to clear the value. Not sure if needed. 
            # elif caption != "+/-":
            else:
                self.value = ''
            self.clear_value_next = False

        # Pressing equal repeatedly should repeat the last equation with the new value moved into previous
        # And the _equal_buffer used as the second value in the equation again.  
        if self.last_pressed == "=":
            # Make the swap needed for it to work
            if caption == '=':
                self.prev_value = self.value
                self.value = self._equals_buffer
            # If using an operator next, we want to carry the result forward to the new equation
            elif caption in self.OPERATORS:
                self.prev_value = self.value
            # Otherwise clear the equal buffer
            else:
                self._equals_buffer = ''
        
        ###                        ###
        # Start the button functions #
        ###                        ### 
        
        # Clear the screen and all the variables
        if caption == 'C':
            self.value = '0'
            self._equals_buffer = ''
            self.last_pressed = ''
            self.prev_value = ''
            self.operator = ''
            self.clear_value_next = True

        elif isinstance(caption, int):
            # If the value is 0, replace it with the new value
            print(self.value)
            if self.value == '0': 
                if caption != 0:    # Dont allow double 0's
                    self.value = str(caption)
            else:
                self.value += str(caption)

        elif caption in self.OPERATORS:
            # Dont recalculate if the last key was = or +/-. or if there was no previous value
            if self.prev_value and not self.last_pressed in ["=", "+/-"]:
                self.value = str(self._evaluate())

            self.operator = caption
            self.prev_value = self.value
            self.clear_value_next = True
        
        elif caption == "=":

            # If = is hit multiple times in a row we want to repeat the last operation 
            # the _equal_buffer stores that value so we can reuse it 
            if not self.last_pressed == "=":
                self._equals_buffer = self.value
            if self.prev_value:
                self.value = str(self._evaluate())
            self.clear_value_next = True

        # We don't want to change the result of an equation to a negative
        elif caption == "+/-" and self.last_pressed != "=":
            # Like with =, we don't want to change the value if we used an operator previously
            if self.last_pressed in self.OPERATORS:
                # Clear the value instead and leave a negative symbol
                self.value = '-'
            elif self.value[0] == "-":
                # Remove symbol if there
                self.value = self.value[1:]
            else:
                # Else add the negative symbol
                self.value = '-' + self.value

        elif caption == "%":
            # Convert the value to a percentage by moving the decimal place
            self.value = str(float(self.value) / 100)

        elif caption == ".":
            # Dont allow multiple decimal places
            if not caption in self.value:
                # Add a leading 0 if decimal on blank value
                if self.value == '':
                    self.value = '0'
                self.value += "."

        # Remove the .0 if self.value is an integer. 
        if self.value[-2:] == '.0':
            self.value = self.value[:-2]
        
        # Prevent bypassing the +/- block after hitting equals
        if caption != "+/-": 
            self.last_pressed = caption

        return self.value
    
    def _evaluate(self):
        return round(eval(self.prev_value + self.operator + self.value),10)