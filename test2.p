/* @(#) %M% %I% %G% @(#) */ 
/*------------------------------------------------------------------------
    File        : sl/lywy-notify.p
    Purpose     :

    Syntax      : RUN sl/lywy-notify.p (INPUT p-transfer-no,INPUT p-rog).

    Description :

    Author(s)   :
    Created     :
    Notes       :
    SW - 22/07/2014 - Update layaway indicator when auto cancel applied.
    SW - 07/10/2014 - Changed label from "Layaway" to "SO/HOLD #".
    SW - 03/11/2014 - Email reminder subject changed.
  ----------------------------------------------------------------------*/ 
/*          This .P file was created with the Progress AppBuilder.      */ 
/*----------------------------------------------------------------------*/ 
.ldfhjk 
DEFINE VARIABLE 

DEFINE VARIABLE 


DEFINE 

/* ***************************  Definitions  ************************** */ 
{fn/address.i} 
{fn/layaway2.i} 
 
{po/purchase-calc.i} 
{fn/fone.i} 
{fn/credit.i} 
{fn/string.i} 

DEFINE INPUT PARAMETER p-transfer-no AS CHARACTER NO-UNDO. 
DEFINE INPUT PARAMETER p-rog         AS CHARACTER NO-UNDO. 

DEFINE TEMP-TABLE tbl-order 
  FIELDS link-order AS CHARACTER 
  INDEX KEY0 AS PRIMARY UNIQUE link-order. 

DEFINE VARIABLE t-error          AS CHARACTER NO-UNDO. 
DEFINE VARIABLE t-to             AS CHARACTER NO-UNDO. 
DEFINE VARIABLE t-from           AS CHARACTER NO-UNDO. 
DEFINE VARIABLE tThanks          AS CHARACTER NO-UNDO. 
DEFINE VARIABLE tsubject         AS CHARACTER NO-UNDO. 
DEFINE VARIABLE cSMSSubject      AS CHARACTER NO-UNDO. 
DEFINE VARIABLE cLanguage        AS CHARACTER NO-UNDO. 
DEFINE VARIABLE t-salesperson    AS CHARACTER NO-UNDO. 
DEFINE VARIABLE X                AS INTEGER   NO-UNDO. 
DEFINE VARIABLE t-deposit        AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE tHold            AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE t-complete       AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE t-email-sent     AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE tFrench          AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE lSendEmail       AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE lOrderNotify     AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE lIsReturnTrans   AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE lPrintMusicOrder AS LOGICAL   NO-UNDO. 
DEFINE VARIABLE tAutoCancel      AS LOGICAL NO-UNDO. 
DEFINE VARIABLE cLsnNumber       AS CHARACTER NO-UNDO. 
DEFINE VARIABLE cSMSNumber       AS CHARACTER NO-UNDO. 
DEFINE VARIABLE cStoreNumber     AS CHARACTER NO-UNDO. 
DEFINE VARIABLE cPickupCode      AS CHARACTER NO-UNDO. 
DEFINE VARIABLE cOrderCode       AS CHARACTER NO-UNDO. 
/*10435 This is a temporary list to accomodate Ontario Curbside Pickup Restrictions */ 
DEFINE VARIABLE cLocCode         AS CHARACTER 
INITIAL "L001,L003,L006,L007,L008,L009,L011,L013,L018,L019,L024,L027,L037,L044,L047,L048,L055,L059,L060,L061,L063,L064,L065,L066,L068,L069,L070,L071,L074,L075,L076,L078,L079,L090" 
NO-UNDO. 

DEFINE BUFFER bf-sale FOR sale. 
DEFINE BUFFER bLocation FOR location. 

DEFINE VARIABLE myStrings AS CLASS fn.Strings NO-UNDO. 

myStrings = NEW fn.Strings(). 

/* ***************************  Main Block  *************************** */ 
DEFINE VARIABLE myWeb   AS CLASS web.WebFunctions. 
DEFINE VARIABLE tWebLoc AS LOGICAL   NO-UNDO. 

myWeb = NEW web.WebFunctions(). 
tWebloc = myWeb:WebLocation(). 
lPrintMusicOrder = myWeb:IsPrintMusicOrder(p-transfer-no). 

/* Task 4045# Do not sent email notification for print music order */ 
IF tWebLoc OR lPrintMusicOrder OR 
   (myWeb:IsAtticSaleOrder(p-transfer-no) AND /* 9589# */ 
    NOT myWeb:SendEmailNotificationForAtticSaleOrders) THEN 
DO: 
  RUN DISABLE. 
  RETURN. 
END. 

IF p-rog = "LINK-ORDER":U THEN 
DO: 
  CREATE tbl-order. 
  ASSIGN 
    tbl-order.link-order = p-transfer-no. 
END. 
ELSE 
DO: 
  FOR EACH transfer-rec NO-LOCK 
    WHERE transfer-rec.transfer-no = p-transfer-no 
    AND transfer-rec.rog = p-rog: 
    FOR EACH transfer-sold OF transfer-rec NO-LOCK 
      WHERE transfer-sold.qty-sold > 0. 
      FIND sale-order OF transfer-sold NO-LOCK NO-ERROR. 
      /*3711 - Do NOT send notification for old transfers*/ 
      IF AVAILABLE sale-order AND sale-order.closed <> YES THEN DO: 
        /* Task 4045# Do not sent email notification for print music order */ 
        IF VALID-OBJECT(myWeb) AND 
           myWeb:IsPrintMusicOrder(sale-order.link-order) THEN 
        DO: 
          RUN DISABLE. 
          RETURN. 
        END. 
        /* 8720# Do not send email notification for ship direct orders */ 
          /* 8812# Send notificaiton for Store generated shipdirect orders */ 
/*        IF CAN-FIND(order OF sale-order WHERE order.shipdirect*/ 
/*                                          AND order.WebGenOrder) THEN                            */ 
/*        DO:                                                   */ 
/*          RUN DISABLE.                                        */ 
/*          RETURN.                                             */ 
/*        END.                                                  */ 
        FIND sale OF sale-order NO-LOCK. 
        IF NOT CAN-FIND(tbl-order WHERE tbl-order.link-order = sale.link-order) 
        THEN 
        DO: 
          CREATE tbl-order. 
          ASSIGN  
            tbl-order.link-order = sale.link-order. 
        END. 
      END. 
    END. 
  END. 
END. 

IF LOOKUP("ORDERALLITEMSNOTIFICATION",SOURCE-PROCEDURE:INTERNAL-ENTRIES) > 0 
  THEN lOrderNotify = DYNAMIC-FUNCTION("ORDERALLITEMSNOTIFICATION" IN SOURCE-PROCEDURE). 
IF lOrderNotify = ? THEN lOrderNotify = FALSE. 


FOR EACH tbl-order: 
  t-email-sent = NO. 
  FIND order OF tbl-order NO-LOCK. 
  FIND location OF order NO-LOCK NO-ERROR.  
  FIND customer OF order NO-LOCK NO-ERROR. 
  cLanguage = IF AVAILABLE customer 
      THEN customer.LanguageCode ELSE location.LanguageCode. 
  tFrench = cLanguage = "FRENCH". 
  myStrings:tLanguage = cLanguage. 
  t-complete = YES. 
  FOR EACH sale OF order WHERE sale.void = NO: 
    FOR EACH sale-order OF sale 
      WHERE sale-order.closed = NO 
      AND sale-order.qty-ordered > sale-order.qty-filled: 
      t-complete = NO. 
      LEAVE. 
    END. 
  END. 
  

  IF IsBinRequired(location.loc-code) THEN 
  DO: 
    RUN DISABLE. 
    RETURN.  /* if bin required eg. web store then don't allocate */ 
  END. 
  
  FIND employee OF order NO-LOCK NO-ERROR. 
  t-salesperson = IF AVAILABLE employee THEN employee.NAME ELSE order.empl-no. 
  ASSIGN 
    tSubject = IF t-complete 
      THEN "LONG & MCQUADE - ORDER HAS ARRIVED" 
      ELSE IF lOrderNotify 
      THEN "LONG & MCQUADE - ORDER CONFIRMATION" 
      ELSE "LONG & MCQUADE - INCOMPLETE ORDER HAS ARRIVED" 
    cSMSSubject = TRIM(ENTRY(2,tSubject,"-")) + " AT". 
    cSMSSubject = myStrings:GetTranslation("","",cSMSsubject). 
  
  /* This should be done before the email block, otherwise it will cancel
     without deposit if no email.  */ 
  tHold = GetOrderHasDepositReason(order.link-order). 

  IF valid-email(order.e-mail,YES,t-error) THEN 
  DO: 
    t-to = order.e-mail. 
    t-deposit = get-order-has-payment(order.link-order). 
    FIND employee OF order NO-LOCK NO-ERROR. 
    t-salesperson = IF AVAILABLE employee THEN employee.NAME ELSE order.empl-no. 
    
    IF NOT corporate-school(order.cust-no) THEN 
    DO: 
      t-email-sent = YES. 
      
      /* send the email 'FROM' the employee */ 
      /* if the employee has no email or is inactive */ 
      /* then use the location email */ 
      IF AVAILABLE employee AND 
      employee.active AND 
      valid-email(employee.e-mail,YES,t-error) THEN 
        t-from = employee.e-mail. 
      ELSE IF valid-email(location.e-mail,YES,t-error) THEN 
        t-from = location.e-mail. 
      ELSE 
        t-from = "INFO@LONG-MCQUADE.COM". 
      
      /* Email sent to the customer */ 
      RUN ss/sendmail.p("PRINT":U, THIS-PROCEDURE 
        ,myStrings:GetTranslation("","",tSubject) 
        ,t-from 
        ,t-to,NO). 
      
      
      myStrings:tLanguage = location.LanguageCode. 
      tSubject = myStrings:GetTranslation("","",tSubject). 
      
      /* Email sent to the employee */ 
      IF AVAILABLE employee AND employee.active AND valid-email(employee.e-mail,YES,t-error) THEN 
      DO: 
        RUN ss/sendmail.p("PRINT":U, THIS-PROCEDURE 
          ,tSubject 
          ,t-from 
          ,employee.e-mail,NO). 
      END. 
    
    END. 
  END.    
  
  /* if the email was not sent as the order has an invalid email or */ 
  /* the order has a valid email and then customer is a corp or school account */ 
  /* send an email to the employee */ 
  IF t-email-sent = NO THEN 
  DO:   
      
    /* send to employee if active otherwise send to store */ 
    IF employee.active AND valid-email(employee.e-mail,YES,t-error) THEN 
      t-to = employee.e-mail. 
    ELSE IF valid-email(location.e-mail,YES,t-error) THEN 
      t-to = location.e-mail. 
    ELSE 
      t-to = "". 
      
    IF corporate-school(order.cust-no) THEN 
      tsubject = "PRODUCTS HAVE ARRIVED FOR THE FOLLOWING CORPORATE/SCHOOL ORDER.". 
    ELSE 
      tsubject = "CONTACT THE FOLLOWING SPECIAL ORDER/HOLD CUSTOMER". 
            
    IF t-to <> "" THEN 
    RUN ss/sendmail.p("PRINT-HOLD-SLIP":U 
      , THIS-PROCEDURE 
      ,myStrings:GetTranslation( 
      tSubject,40,"L":U) 
      ,t-to   /* THIS IS THE FROM */ 
      ,t-to,NO). 
  END. 
  
  
  /* Task 5234# Send SMS notification */ 
  IF AVAILABLE location THEN 
  DO: 
    DEFINE VARIABLE cSMSText AS CHARACTER NO-UNDO. 
    DEFINE VARIABLE cLocName AS CHARACTER NO-UNDO. 
    DEFINE VARIABLE oSMS AS CLASS server.SMS NO-UNDO. 
    oSMS = NEW server.SMS(location.loc-code,order.cust-no). 
    ASSIGN 
      oSMS:TranslationRequired = FALSE 
      cLocName = location.name 
      myStrings:tLanguage = cLanguage. 
      
    cLocName = myStrings:ProperName(cLocName," "). 
    IF NUM-ENTRIES(cLocName,".") > 0 
      THEN cLocName = myStrings:ProperName(cLocName,"."). 
    IF NUM-ENTRIES(cLocName,"-") > 0 
      THEN cLocName = myStrings:ProperName(cLocName,"-").     
    cLocName = "LONG & MCQUADE " + cLocName. 
        
    /* 8475 */ 
    IF tSubject = "LONG & MCQUADE - INCOMPLETE ORDER HAS ARRIVED" OR 
       tSubject =  "LONG & MCQUADE - ORDER HAS ARRIVED" THEN DO: 
      IF tFrench THEN 
        cSMSsubject = cSMSSubject 
        + " " + cLocName 
        + ". " 
        + "UN COURRIEL QUI VOUS EXPLIQUE COMMENT L OBTENIR VOUS A ÉTÉ ENVOYÉ.". 
      ELSE 
        cSMSsubject = cSMSSubject 
        + " " + cLocName 
        + ". " 
        + myStrings:GetTranslation("","","PLEASE CHECK YOUR EMAIL FOR INSTRUCTIONS ON OBTAINING YOUR ORDER."). 
      END. 
    ELSE DO:        
        cSMSsubject = cSMSSubject 
        + " " + cLocName 
        + ". " 
        + myStrings:GetTranslation("","","FOR MORE INFORMATION CALL") 
        + " " + location.telephone. 
    END. /* IF tSubject */ 
               
    oSMS:SEND(cSMSSubject). 
    DELETE OBJECT oSMS. 
  END. 

END. 

IF LOOKUP("NOTIFYCUSTOMER",SOURCE-PROCEDURE:INTERNAL-ENTRIES) > 0 AND 
   DYNAMIC-FUNCTION("NOTIFYCUSTOMER" IN SOURCE-PROCEDURE) 
  THEN RETURN. 
  
FOR EACH tbl-order: 
  FIND order OF tbl-order NO-LOCK. 

  IF order.e-mail = ? OR corporate-school(order.cust-no) THEN NEXT. 
  t-deposit = get-order-has-payment(tbl-order.link-order). 
  tHold = GetOrderHasDepositReason(order.link-order). 

  FOR EACH order-i OF order WHERE order-i.qty > 0 
    AND order-i.sku-no <> 65 
    AND order-i.item-type <> "RS":U: 
    RUN get-saleorder(order-i.link-order,order-i.item-no,BUFFER sale-order). 
    IF AVAILABLE sale-order THEN 
    DO: 
      IF sale-order.qty-ordered > sale-order.qty-filled THEN X = X + 1. 
    END. 
    ELSE X = X + 1. 
  END. 

  /*
  IF (t-deposit = NO AND tHold = NO)
    OR CAN-FIND(FIRST ord-lywy WHERE ord-lywy.link-order = order.link-order
      AND ord-lywy.MiniReason = "not held") THEN DO TRANSACTION:
      */ 

  ASSIGN tAutoCancel = NO. 
  IF (t-deposit = NO AND 
    NOT order.ShipDirect AND /* 8720 */ 
    (tHold = NO OR 
    CAN-FIND(FIRST ord-lywy WHERE ord-lywy.link-order = order.link-order 
    AND ord-lywy.MiniReason = "NOT HELD":U)) AND 
    /* Task# 3772. For a special order return, the above condition will satisfy.
       If the last sale is return then do not cancel the order */ 

    NOT CAN-FIND(LAST sale OF order 
      WHERE sale.sale-type = "RT" 
        AND sale.dt-trans = TODAY)) THEN 
  DO TRANSACTION: 

    IF X < 1 THEN 
    DO: 
      ASSIGN tAutoCancel = YES. 
      RUN cancel. /* cancel whole layaway */ 
    END. 
    ELSE 
    DO: /* cancel this item change only */ 
      RUN ps/cr-sale1.p 
        ("08":U 
        ,"TJ":U 
        ,order.cust-no 
        ,BUFFER order 
        ,BUFFER bf-sale). 
      FOR EACH order-i OF order NO-LOCK 
        WHERE order-i.qty <> 0: 
        RUN get-saleorder(order-i.link-order,order-i.item-no,BUFFER sale-order). 
        IF AVAILABLE sale-order AND sale-order.qty-filled > 0 THEN NEXT. 
        RELEASE sale-i. 
        BUFFER-COPY order-i TO sale-i 
          ASSIGN 
          sale-i.link-sale = bf-sale.link-sale 
          sale-i.info-item = NO 
          sale-i.link-item = order-i.item-no. 
        FOR EACH order-s OF order-i NO-LOCK: 
          RELEASE sale-s. 
          BUFFER-COPY order-s TO sale-s. 
          ASSIGN 
            sale-s.link-sale = bf-sale.link-sale. 
        END. 
      END. 
      RUN commit. 
    END. 
  END. 

  /* ON AUTO CANCEL UPDATE CUSTOMER "FLAGS" ON SEARCH BROWSER. TASK# 3657 */ 
  IF tAutoCancel = YES THEN 
  DO: 
    FIND customer NO-LOCK 
      WHERE customer.cust-no = order.cust-no NO-ERROR. 
    IF AVAILABLE customer 
      /* THIS IS THE ACTUAL UPDATE OF THE "FLAGS" */ 
      THEN RUN sl/customer-tn.p(BUFFER customer, order.sale-type). 
  END. 

END. 
DELETE OBJECT myStrings. 




/* **********************  Internal Procedures  *********************** */ 


PROCEDURE DISABLE: 
  /*--------------------------------------------------------------------------
    Purpose:
    Notes:
  ---------------------------------------------------------------------------*/ 
  RUN ss/destroy-all-super-proc.p. 

END PROCEDURE. 
        
PROCEDURE cancel : 
  /*--------------------------------------------------------------------------
    Purpose:     
    Parameters:  <none>
    Notes:
  --------------------------------------------------------------------------*/ 
  DEFINE BUFFER bf-sale FOR sale. 
  DEFINE BUFFER bf-cust FOR customer. 
  DEFINE BUFFER bf-ord FOR order. 
  
  DEFINE VARIABLE t-item-no AS INTEGER   NO-UNDO INITIAL 1. 
  DEFINE VARIABLE t-doc     AS CHARACTER NO-UNDO. 
  RUN ps/cr-sale1.p  
    ("09":U 
    ,"TJ":U 
    ,order.cust-no 
    ,BUFFER order 
    ,BUFFER bf-sale). 
  ASSIGN 
    bf-sale.prev-order-bal = get-order-balance(order.link-order) 
    bf-sale.prev-order-pay = 0. 

  FOR EACH order-i OF order NO-LOCK WHERE order-i.qty <> 0: 
    CREATE sale-i. 
    BUFFER-COPY order-i TO sale-i 
      ASSIGN 
      sale-i.link-sale = bf-sale.link-sale 
      /*        sale-i.item-no   = t-item-no */ 
      /*        sale-i.info-item = NO   /* set to no so calc-tax will work */ */ 
      sale-i.retail   = - order-i.retail 
      sale-i.pos-mkdn = - order-i.pos-mkdn 
      sale-i.mkdn-amt = - order-i.mkdn-amt 
      sale-i.disc-amt = - order-i.disc-amt 
      sale-i.pos-disc = - order-i.pos-disc 
      sale-i.qty      = - order-i.qty 
      t-item-no = t-item-no + 1. 
    FOR EACH order-s OF order-i NO-LOCK: 
      CREATE sale-s. 
      ASSIGN 
        sale-s.LINK-SALE = sale-i.LINK-SALE 
        sale-s.ITEM-NO   = sale-i.ITEM-NO 
        sale-s.LINE-NO   = order-s.LINE-NO 
        sale-s.SERIAL-NO = order-s.SERIAL-NO. 
      IF sale-i.serial-no = "" THEN sale-i.serial-no = sale-s.serial-no. 
    END. 
    t-doc = sale-i.link-sale + "-":U + STRING(sale-i.item-no). 
    RUN im/last-doc.p("SET":U,INPUT-OUTPUT t-doc). 
    RUN get-saleorder(order-i.link-order,order-i.item-no,BUFFER sale-order). 
    IF NOT AVAILABLE sale-order THEN 
    DO:        
      update-onlywy(sale-i.sku-no,order.loc-code 
        ,sale-i.qty,sale-i.used-flag = "U":U,sale-i.serial-no 
        ,sale-i.reason-code 
        ,order.order-no + "-":U + STRING(order-i.item-no) 
        ,YES). 
    END. 
  END. 
  RUN ps/calc-tax.p(BUFFER bf-sale). 
  FOR EACH sale-i OF bf-sale EXCLUSIVE-LOCK: 
    /* must set info-item after the tax calc */ 
    sale-i.info-item = YES. 
  END. 
  RUN ps/can-lywy-prepays.p (BUFFER bf-sale). 
  RUN ps/upd-saleorder.p(order.link-order,bf-sale.link-sale,YES). 

  FIND CURRENT order EXCLUSIVE-LOCK NO-ERROR. 
  order.int-status = "CN":U. 
  
  FIND bf-cust OF order NO-LOCK NO-ERROR. 
  IF AVAILABLE bf-cust AND INDEX(bf-cust.tn,"L") <> 0 THEN 
  DO: 
    FIND FIRST bf-ord OF bf-cust 
      WHERE bf-ord.sale-type = "LY" 
        AND bf-ord.int-status = "" NO-LOCK NO-ERROR. 
    IF NOT AVAILABLE bf-ord THEN 
    DO: 
      FIND bf-cust OF order EXCLUSIVE-LOCK NO-WAIT NO-ERROR. 
      IF AVAILABLE bf-cust THEN 
        ASSIGN 
          bf-cust.tn = REPLACE(bf-cust.tn,"L",""). 
    END.  
  END.    
  
  bf-sale.void = NO. 
END PROCEDURE. 

PROCEDURE commit : 
  /*--------------------------------------------------------------------------
    Purpose:     
    Parameters:  <none>
    Notes: 
  --------------------------------------------------------------------------*/ 

  DEFINE VARIABLE t-ans       AS LOGICAL       NO-UNDO. 
  DEFINE VARIABLE t-delta     AS DECIMAL   NO-UNDO. 
  DEFINE VARIABLE t-sale-qty  AS DECIMAL   NO-UNDO. 
  DEFINE VARIABLE t-order-qty AS DECIMAL   NO-UNDO. 
  DEFINE VARIABLE t-doc       AS CHARACTER NO-UNDO. 
  
  DO TRANS:  /* commit payment to database  */ 
    FIND order WHERE order.link-order = bf-sale.link-order EXCLUSIVE-LOCK 
      NO-ERROR. 
    order.int-status = "":U. 
  
    FIND FIRST customer-r NO-LOCK 
      WHERE customer-r.cust-no = bf-sale.cust-no NO-ERROR. 
  
    FIND CURRENT bf-sale EXCLUSIVE-LOCK NO-ERROR. 
    ASSIGN 
      bf-sale.prev-order-pay = get-order-balance(order.link-order) 
      bf-sale.prev-order-bal = get-order-balance(order.link-order) 
      bf-sale.cust-loc       = IF AVAILABLE customer-r 
                          THEN customer-r.loc-code ELSE bf-sale.cust-loc. 
  
    /* update balance on movement sale sale */ 
    /* set all the items on the movement sale as info item
                              so they don't effect sales */ 
    FOR EACH sale-i OF bf-sale EXCLUSIVE-LOCK: 
      sale-i.info-item = YES. 
      IF sale-i.used-flag = "U":U 
        AND CAN-FIND(sale-order OF sale-i) THEN sale-i.used-flag = "":U. 
    END. 
  
    /* unvoid sale for inventory movement */ 
    RUN ps/unvoid.p(BUFFER bf-sale). 
    
    /*RUN ps/unvoid-pay-sched.p (BUFFER bf-sale).*/ 
    /*RUN ps/unvoid-pay-sched.p (BUFFER sale).*/ 
    IF CAN-FIND(FIRST pay-sched NO-LOCK 
      WHERE pay-sched.cust-no = bf-sale.cust-no 
      AND pay-sched.link-sale = bf-sale.link-sale 
      AND pay-sched.link-order = bf-sale.link-order 
      AND pay-sched.void = YES 
      /* USE-INDEX voided */) 
      THEN RUN sl/void-old-pay-sched.p (BUFFER bf-sale). 
    RUN ps/unvoid-pay-sched.p (BUFFER bf-sale). 
    
    RUN ps-pos-cus.p(RECID(bf-sale),RECID(customer),"LAYAWAY":U). 
    /*
    IF AVAIL sale THEN DO: /* unvoid payment sale */ 
      message sale.loc-code sale.reg-no sale.trans-no
        view-as alert-box.v
      pause 102.
      run ps/unvoid.p(buffer sale).
      run ps-pos-cus.p(recid(sale),recid(customer),"layaway":U).
    END.
    */ 
    /* update the order by first delete on the details and then copy 
       the sale items to the order item table  */ 
    FOR EACH order-i OF order EXCLUSIVE-LOCK: 
      FIND sale-i OF bf-sale WHERE sale-i.item-no = order-i.item-no 
        AND sale-i.link-item = order-i.item-no 
        NO-LOCK NO-ERROR. 
      IF NOT AVAILABLE sale-i THEN 
      DO: 
        RUN get-saleorder(order-i.link-order,order-i.item-no,BUFFER sale-order). 
        /*
        if avail sale-order then cr-req-msg(sale-order.sale-ord-id,"CN").
        */ 
        IF NOT AVAILABLE sale-order THEN 
        DO: 
          t-doc = bf-sale.link-sale + "-":U + STRING(order-i.item-no). 
          RUN im/last-doc.p("SET":U,INPUT-OUTPUT t-doc). 
          update-onlywy(order-i.sku-no,order.loc-code 
            ,- order-i.qty,order-i.used-flag = "U":U,order-i.serial-no 
            ,order-i.reason-code 
            ,order.order-no + "-":U + STRING(order-i.item-no) 
            + "-DELETED-LYWY":U 
            ,YES). 
        END. 
        DELETE order-i. 
      END. 
    END. 
    FOR EACH order-s OF order EXCLUSIVE-LOCK: 
      DELETE order-s. 
    END. 
  
    FOR EACH sale-i OF bf-sale NO-LOCK 
      WHERE sale-i.item-type <> "TX":U 
      AND NOT sale-i.void: 
      FIND order-i EXCLUSIVE-LOCK 
        WHERE order-i.link-order = bf-sale.link-order 
        AND order-i.item-no = sale-i.item-no 
        NO-ERROR. 
      
      t-sale-qty  = sale-i.qty. 
      t-order-qty = IF NOT AVAILABLE order-i THEN 0 
      ELSE order-i.qty. 
      t-delta = t-sale-qty - t-order-qty. 
      IF AVAILABLE order-i THEN 
      DO: 
        RUN get-saleorder(order-i.link-order,order-i.item-no,BUFFER sale-order). 
        IF AVAILABLE sale-order THEN 
        DO: 
          cr-req-msg(sale-order.sale-ord-id,"CQ":U 
            ,INTEGER(sale-i.qty - sale-order.qty-ordered)). 
          t-delta = 0. 
        END. 
      END. 
      ELSE t-delta = sale-i.qty. 

      t-doc = sale-i.link-sale + "-":U + STRING(sale-i.item-no). 
      RUN im/last-doc.p("SET":U,INPUT-OUTPUT t-doc). 
      BUFFER-COPY sale-i TO order-i 
        ASSIGN 
        order-i.link-order = bf-sale.link-order 
        order-i.info-item = NO 
        order-i.EXTENDED = sale-i.retail 
                           + sale-i.pos-disc 
                           + sale-i.pos-mkdn 
                           + sale-i.mkdn-amt 
                           + sale-i.disc-amt. 
      IF t-delta <> 0 
        THEN update-onlywy 
          (order-i.sku-no,order.loc-code 
          ,t-delta,order-i.used-flag = "U":U 
          ,sale-i.serial-no 
          ,order-i.reason-code 
          ,sale-i.link-sale + "-":U + STRING(sale-i.item-no),YES). 
      IF sale-i.used-flag = "U":U AND sale-i.item-type <> "RT":U THEN 
      DO: 
        FIND inv-locsrl OF sale-i EXCLUSIVE-LOCK NO-ERROR. 
        IF AVAILABLE inv-locsrl 
          AND inv-locsrl.doc-ref = bf-sale.loc-code + "-":U 
          + bf-sale.reg-no   + "-":U 
          + STRING(bf-sale.trans-no) 
          THEN inv-locsrl.i-status = 1. 
      END. 
    END. 
    FOR EACH sale-s OF bf-sale NO-LOCK: 
      RELEASE order-s. 
      BUFFER-COPY sale-s TO order-s 
        ASSIGN 
        order-s.link-order = order.link-order. 
    END. 
    RUN ps/upd-saleorder.p(order.link-order,bf-sale.link-sale,NO). 
  END. /* end of transaction */ 
  DO TRANSACTION: /*  this must be in its own transaction so that the */ 
    /* Triggers fire before running this programs. */ 
    RUN sl/customer-tn.p(BUFFER customer,"ALL":U). 
  END. 
END PROCEDURE. 

PROCEDURE get-saleorder : 
  /*--------------------------------------------------------------------------
    Purpose:     
    Parameters:  <none>
    Notes:       
  --------------------------------------------------------------------------*/ 
 
  DEFINE INPUT PARAMETER p-linkorder AS CHARACTER NO-UNDO. 
  DEFINE INPUT PARAMETER p-item AS INTEGER NO-UNDO. 
  DEFINE PARAMETER BUFFER b-sale-order FOR sale-order. 

  DEFINE           BUFFER b-sale       FOR sale. 

  FOR EACH b-sale WHERE b-sale.link-order = p-linkorder NO-LOCK: 
    FIND b-sale-order WHERE b-sale-order.link-sale = b-sale.link-sale 
      AND b-sale-order.item-no = p-item 
      NO-LOCK NO-ERROR. 
    IF AVAILABLE b-sale-order THEN RETURN. 
  END. 

END PROCEDURE. 

PROCEDURE Print: 
  DEFINE VARIABLE cOrder AS CHARACTER NO-UNDO. 
  DEFINE VARIABLE lNoStock AS LOGICAL NO-UNDO. 
  
  DEFINE BUFFER customer FOR customer. 
  DEFINE BUFFER na-info FOR na-info. 
     
  FIND customer OF order NO-LOCK NO-ERROR. 
  FIND na-info OF customer NO-LOCK NO-ERROR. 

  ASSIGN 
    tHold = IF CAN-FIND(FIRST ord-lywy 
                 WHERE ord-lywy.link-order = order.link-order 
                   AND ord-lywy.MiniReason = "NOT HELD") 
             THEN NO ELSE tHold 
    cOrder = IF order.WebGenOrder AND order.web-order-no <> ""  /*9964# */ 
               THEN order.web-order-no ELSE order.order-no. 
  PUT UNFORMATTED    
     myStrings:GetTranslation("","","HELLO ") SPACE(1) 
     na-info.NAME  "," SKIP(2). 
  
  IF t-deposit OR (t-deposit = NO AND tHold = YES) THEN 
  DO: 
    /* All items are ready for pickup */ 
    IF t-complete THEN 
      DO: 
        /* 8812# Sent shipdirect specific email to customers */ 
        IF order.ShipDirect 
          THEN PUT UNFORMATTED 
            REPLACE(myStrings:Gettranslation( 
              "YOUR ORDER (&1) HAS ARRIVED. YOUR ORDER WILL BE SHIPPED OUT SHORTLY.",90,"L") 
                    ,"&1",cOrder) 
             SKIP(2). 
          ELSE DISPLAY 
            REPLACE(myStrings:Gettranslation("ORDER (&1) HAS ARRIVED.",35,"L") 
                    ,"&1",cOrder) FORMAT "X(50)" 
            SKIP(2) 
            WITH NO-BOX NO-LABELS FRAME fr-head1. 
    END. 
  
    /* Some items are ready for pickup */ 
    ELSE 
    DO: 
      IF lOrderNotify 
        THEN PUT UNFORMATTED  
            REPLACE(myStrings:GetTranslation("THE PRODUCT(S) YOU HAVE CHOSEN TO PICK UP " 
            + "IN-STORE ARE CURRENTLY NOT AVAILABLE AT YOUR CHOSEN STORE. A SPECIAL " 
            + "ORDER &1 HAS BEEN PLACED FOR YOU AND YOU WILL BE EMAILED WHEN THE " 
            + "PRODUCT(S) ARRIVE AT THE STORE.",300,"L") 
            ,"&1",cOrder) SKIP(2). 
        ELSE DO: 
          IF order.ShipDirect 
            THEN 
              PUT UNFORMATTED  
                REPLACE(myStrings:GetTranslation( 
                  "SOME, BUT NOT ALL, OF ORDER (&1) HAS ARRIVED. " 
                  + "NORMALLY WE WILL SHIP THE ORDER WHEN EVERYTHING ARRIVES, " 
                  + "IF YOU WOULD LIKE A PARTIAL SHIPMENT PLEASE CONTACT THE " 
                  + "STORE. ",200,"L") 
                  ,"&1",cOrder) 
              SKIP(2). 

            ELSE 
              DISPLAY 
                REPLACE(myStrings:GetTranslation( 
                  "SOME, BUT NOT ALL, OF ORDER (&1) HAS ARRIVED.",60,"L") 
                  ,"&1",cOrder) FORMAT "X(60)" 
              SKIP(2) 
              WITH NO-BOX NO-LABELS FRAME fr-head2. 
        END.   
    END. 
    IF NOT order.ShipDirect THEN 
    DO:  
      /* 11299 */ 
      IF tfrench THEN 
             PUT UNFORMATTED "". 
          ELSE 
      DO:     
               
                IF CAN-DO(cLocCode,order.loc-code) THEN 
                DO: 
                    /* 10435 Retreive the Phone Numbers and SMS Numbers for each location */ 
                        FIND FIRST blocation NO-LOCK 
                          WHERE blocation.loc-code = order.loc-code NO-ERROR. 
                        IF AVAILABLE blocation THEN 
                          ASSIGN 
                                cLsnNumber = blocation.lsn-num 
                                cSmsNumber = blocation.sms-num 
                                cStoreNumber = blocation.telephone. 
                                                                                                                           
                        
                END.                          
                                                  
       END. 
     
    END.      
    /* Print line items */ 
    RUN print-items(YES). 
/*    PUT UNFORMATTED SKIP(2).*/ 
    IF NOT t-complete AND 
       NOT lOrderNotify AND 
       NOT order.ShipDirect /* 8812# */ 
      THEN PUT UNFORMATTED 
          SKIP (2) 
          myStrings:GetTranslation( 
          "YOU CAN EITHER COME BY THE STORE AND PICKUP WHAT IS AVAILABLE " 
          + "OR YOU CAN WAIT AND WE WILL CONTACT YOU WHEN THE REST OF THE " 
          + "ORDER HAS ARRIVED.",170,"L"). 

    RUN DisplayFooter.  
  END. /* IF t-deposit OR  */ 
  ELSE DO: 
   
    /* Product available which customer has shown interest in */ 
    IF t-complete THEN 
    DO: 
      DISPLAY 
        myStrings:Gettranslation( 
        "THE PRODUCT IN WHICH YOU HAVE EXPRESSED INTEREST IS NOW IN STOCK.",70,"L") 
        FORMAT "X(70)" 
        SKIP(2) 
      WITH FRAME fr-no-deposit WIDTH-CHARS 132 NO-BOX NO-LABELS.  
    END. 

    /* Product available which customer has shown interest (few products are in stock) */ 
    ELSE DO: 
      DISPLAY 
        myStrings:Gettranslation( 
        "ONE OR MORE OF THE PRODUCTS IN WHICH YOU HAVE EXPRESSED INTEREST " 
        + "IS NOW IN STOCK.",85,"L") FORMAT "X(85)" 
        
        SKIP(2) 
      WITH FRAME fr-no-deposit1 WIDTH-CHARS 132 NO-BOX NO-LABELS. 
    END. 
    /* Print line items */ 
    RUN print-items (NO). 
    IF t-complete 
      THEN PUT  UNFORMATTED SKIP(1) 
        myStrings:GetTranslation( 
        "IF YOU WISH TO PURCHASE OR TRY THIS PRODUCT PLEASE CONTACT " 
        + "THE STORE TO MAKE THE NECESSARY ARRANGEMENTS.",120,"L"). 
    RUN DisplayFooter.      
  END. 
  
END PROCEDURE.  /* Print */ 

PROCEDURE print-hold-slip : 

  /*--------------------------------------------------------------------------
    Purpose:     
    Parameters:  <none>
    Notes:       
  --------------------------------------------------------------------------*/ 
  DEFINE VARIABLE x            AS INTEGER   NO-UNDO. 
  DEFINE VARIABLE t-note       AS CHARACTER NO-UNDO. 
  DEFINE VARIABLE t-otheritems AS LOGICAL       NO-UNDO. 
  DEFINE VARIABLE t-more       AS LOGICAL       NO-UNDO. 
  DEFINE VARIABLE t-newline    AS LOGICAL       NO-UNDO. 
  DEFINE VARIABLE t-deposit    AS DECIMAL   NO-UNDO. 

  DEFINE BUFFER bf-saleorder FOR sale-order. 
  DEFINE BUFFER bf-sale      FOR sale. 


  FIND customer   OF order      NO-LOCK. 
  FIND na-info    OF customer   NO-LOCK. 

        
  FOR EACH bf-sale OF order NO-LOCK WHERE NOT bf-sale.void: 
    FOR EACH bf-saleorder OF bf-sale NO-LOCK 
      WHERE bf-saleorder.item-no <> sale-order.item-no 
      AND bf-saleorder.qty-filled < bf-saleorder.qty-ordered : 
      t-otheritems = YES. 
    END. 
  END. 
  t-deposit = get-order-pay-tot(order.link-order). 
  tHold = IF CAN-FIND(FIRST ord-lywy 
    WHERE ord-lywy.link-order = order.link-order 
    AND (ord-lywy.MiniReason <> "NOT HELD":U 
    AND ord-lywy.MiniReason <> "") ) 
    THEN YES ELSE NO. 

  DISPLAY 
    (IF t-deposit = 0 AND tHold = NO 
    AND order.e-mail <> ? 
    THEN myStrings:GetTranslation("","","AUTO-CANCELLED SO/HOLD") ELSE "") 
      FORMAT "X(30)" SKIP(1) 
    REPLACE(CAPS(myStrings:GetTranslation("","","SP ORD/HOLD#")),":","") 
      FORMAT "X(12)" ":" order.order-no        SKIP    
    REPLACE(CAPS(myStrings:GetTranslation("","","CUSTOMER")),":","") 
      FORMAT "X(12)" ":" na-info.NAME          SKIP 
    REPLACE(CAPS(myStrings:GetTranslation("","","TELEPHONE")),":","") 
      FORMAT "X(12)" ":" STRING(phone-disp(na-info.telephone),phone-format()) 
    FORMAT "X(15)"   SKIP 
    REPLACE(CAPS(myStrings:GetTranslation("","","WORK#       :")),":","") 
      FORMAT "X(12)" ":" STRING(phone-disp(na-info.telephone-w),phone-format()) 
    FORMAT "X(15)"  SKIP 
    REPLACE(CAPS(myStrings:GetTranslation("","","CELL#       :")),":","") 
      FORMAT "X(12)" ":" STRING(phone-disp(na-info.cell-no),phone-format())    
    FORMAT "X(15)"   SKIP 
    REPLACE(CAPS(myStrings:GetTranslation("","","DEPOSIT AMT :")),":","") 
      FORMAT "X(12)" ":" t-deposit SKIP 
    REPLACE(CAPS(myStrings:GetTranslation("","","SALESPERSON :")),":","") 
      FORMAT "X(12)" ":" t-salesperson FORMAT "X(30)" SKIP 
    WITH FRAME fr-hold WIDTH-CHARS 132 NO-BOX NO-LABELS. 
  
  /* #15244 Removed printing of special notes.*/ 
  RUN print-items(YES). 
END PROCEDURE. 
 
PROCEDURE print-items : 
  /*--------------------------------------------------------------------------
    Purpose:     
    Parameters:  <none>
    Notes:       
  --------------------------------------------------------------------------*/ 
  DEFINE INPUT PARAMETER p-qty AS LOGICAL NO-UNDO. 

  DEFINE VARIABLE t-ysl-bstock  AS LOGICAL     NO-UNDO. 
  DEFINE VARIABLE t-qty-ordered AS DECIMAL NO-UNDO. 
  DEFINE VARIABLE t-filled      AS INTEGER NO-UNDO. 
  DEFINE VARIABLE cPickupStore  AS CHARACTER NO-UNDO. 

  DEFINE BUFFER location FOR location. 
  DEFINE BUFFER sale-order FOR sale-order. 
  
  IF p-qty THEN 
  DO: 
    IF tfrench THEN 
    DO: 
      DISPLAY 
        "                                                                                                                                               " 
        /* RIGHT JUSTIFY THE REÇU COLUMN HEADING. TASK# 4719 */ 
        "MARQUE               MODÈLE           DESCRIPTION                              COMMANDÈ       REÇU SUCCURSALE                                  " 
        "-------------------- ---------------- ---------------------------------------- -------- ---------- --------------------------------------------":U 
        WITH FRAME fr-depositlabelsFrench NO-BOX NO-LABELS WIDTH-CHARS 155. 
    END. 
    ELSE 
    DO: 
/*      DISPLAY*/ 
      PUT UNFORMATTED 
        "                                                                               QTY      QTY READY                                              " SKIP. 
      IF NOT order.ShipDirect 
        THEN PUT UNFORMATTED   
        "BRAND                MODEL            DESCRIPTION                              ORDERED  FOR PICKUP PICKUP STORE                                " SKIP. 
        ELSE PUT UNFORMATTED  
        "BRAND                MODEL            DESCRIPTION                              ORDERED  TO SHIP    SHIPPING STORE                                " SKIP.   
      PUT UNFORMATTED 
        "-------------------- ---------------- ---------------------------------------- -------- ---------- --------------------------------------------" SKIP . 
/*        WITH FRAME fr-depositlabels NO-BOX NO-LABELS WIDTH 155.*/ 
    END. 
    FOR EACH order-i OF order NO-LOCK 
      WHERE order-i.item-type <> "RS":U 
      AND order-i.sku-no <> 0: 

      /* 8934# Exclude shipping skus */        
      IF VALID-OBJECT(myWeb) THEN 
      DO: 
        IF order-i.sku-no  = myWeb:ShippingAllowance THEN NEXT. 
        IF order-i.sku-no = myWeb:ShippingInsurance THEN NEXT. 
        IF order-i.sku-no = myWeb:ShippingSku THEN NEXT. 
      END. 
        
      FIND inv-master OF order-i NO-LOCK. 
      FIND brand OF inv-master NO-LOCK. 
      t-filled = get-qty-filled(order-i.link-order 
        ,order-i.item-no 
        ,t-qty-ordered 
        ,t-ysl-bstock). 
      RUN get-saleorder(order-i.link-order,order-i.item-no,BUFFER sale-order). 
      IF AVAILABLE sale-order 
        THEN cPickupStore = IF sale-order.type = "PICKUP OTHER STORE" 
            THEN sale-order.get-from-loc ELSE sale-order.loc-code. 
        ELSE cPickupStore = order.loc-code. 
         
      FIND location 
        WHERE location.loc-code = cPickupStore NO-ERROR. 
      IF t-filled = 0 AND 
         t-complete AND 
         AVAILABLE sale-order 
         THEN t-filled = sale-order.qty-filled. 
           
      cPickupStore = IF AVAILABLE location AND 
                     t-filled > 0 
          THEN TRIM(location.address[1]) 
               + ", " 
               + TRIM(location.address[2]) 
          ELSE "". 
      DISPLAY 
        brand.brand-desc 
        inv-master.product-no 
        order-i.DESCRIPTION FORMAT "X(40)":U SPACE(2) 
        /* If the order is completely picked up, the order-i.qty field is zeroed out.
           In such instance, check the t-complete flag. If t-complete is true, then
           use sale-order.qty-ordered instead. */ 
        (IF order-i.qty = 0 AND 
            t-complete AND 
            AVAILABLE sale-order 
            THEN sale-order.qty-ordered 
            ELSE order-i.qty) FORMAT "->>>>>9" 
        WHEN p-qty 
        t-filled    FORMAT "->>>>>>>>9":U 
        WHEN p-qty 
        cPickupStore FORMAT "X(45)" 
        WITH FRAME fr-detail NO-LABELS WIDTH-CHARS 155 NO-BOX. 
    END. 
  END. 
  ELSE 
  DO: 
    IF tfrench THEN 
    DO: 
      DISPLAY 
        CAPS("                                                                              ") FORMAT "X(155)" 
        CAPS("MARQUE               MODÈLE           DESCRIPTION                             ") FORMAT "X(155)" 
             "-------------------- ---------------- ----------------------------------------":U FORMAT "X(155)" 
        WITH FRAME fr-no-depositlabels1French NO-BOX NO-LABELS WIDTH-CHARS 155. 
    END. 
    ELSE 
    DO: 
      DISPLAY 
        "                                                                              " 
        "BRAND                MODEL            DESCRIPTION                             " 
        "-------------------- ---------------- ----------------------------------------":U 
        WITH FRAME fr-no-depositlabels1 WIDTH-CHARS 155 NO-BOX. 
    END. 
    FOR EACH order-i OF order NO-LOCK 
      WHERE order-i.item-type <> "RS":U 
      AND order-i.sku-no <> 0: 
      
            /* 8934# Exclude shipping skus */        
      IF VALID-OBJECT(myWeb) THEN 
      DO: 
        IF order-i.sku-no  = myWeb:ShippingAllowance THEN NEXT. 
        IF order-i.sku-no = myWeb:ShippingInsurance THEN NEXT. 
        IF order-i.sku-no = myWeb:ShippingSku THEN NEXT. 
      END. 
        
      FIND inv-master OF order-i NO-LOCK. 
      FIND brand OF inv-master NO-LOCK. 
      DISPLAY 
        brand.brand-desc 
        inv-master.product-no 
        order-i.DESCRIPTION FORMAT "X(40)":U 
        WITH FRAME fr-detail1 NO-LABELS WIDTH-CHARS 155 NO-BOX. 
    END. 
  END. 
END PROCEDURE. 

PROCEDURE DisplayFooter: 
  DEFINE VARIABLE cMsg          AS CHARACTER NO-UNDO. 
  DEFINE VARIABLE t-co-loc-name AS CHARACTER NO-UNDO. 
  
  RUN login-info.p ('company-location-name',OUTPUT t-co-loc-name). 
  cMsg = myStrings:GetTranslation("IF YOU HAVE ANY QUESTIONS, PLEASE CONTACT:",55,"L"). 
  DISPLAY 
    SKIP (2) 
    cMsg FORMAT "X(70)" 
    SKIP(2) 
    t-salesperson FORMAT "X(40)" SKIP 
    t-co-loc-name FORMAT "X(40)" SKIP 
    location.telephone SKIP(2) 
    /* Translation table contains a value Thanks,. Instead of 
       creating a new lookupvalue for Thanks with an !, simply
       use the existing one and replace the comma */ 
    REPLACE(myStrings:Gettranslation("","","THANKS,"),",","!") 
    WITH FRAME fr-mail NO-LABELS NO-BOX.  
END PROCEDURE. 

FINALLY: 
  IF VALID-OBJECT(myWeb) THEN DELETE OBJECT myWeb. 
END FINALLY. 

