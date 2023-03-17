import re

pattern = r"""(?:(?:'|")?F[1-9](?:'|")?)|(?:(?:'|")?F1[0-2](?:'|")?)"""
text = """
ON "F3" 
OF 'f12'
ON F3


/* @(#) SchRegtot.p 1.90 05/10/17 @(#) */ 
/*---------------------------------------------------------------------------- 
  File: 
    SchRegtot.p 

  Description: 
    <description>

  Syntax: 
    RUN SchRegtot.p 
      (input-output t-deposit, p-orderid, input-output t-pay-enter, 
       input-output t-dt-enter, t-paid, r-ins, 
       input f9active, tSchCostShare, tSchCostShareValue, 
       output discount, output is_charge, output discreason, 
       output t-disc-type,   /* send with regtot.p */ 
       """

matches = list(re.finditer(pattern, text))

for match in matches:
    print(match.group())