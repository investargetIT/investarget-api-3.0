#coding=utf-8


userpermfield = {
    'usersys.admin_changeuser':[],
    'usersys.trader_changeuser':['IR','createuser','createdtime'],
    'usersys.admin_adduser':[],
    'usersys.trader_adduser':['IR'],
    'changeself':['groups','IR','createuser','createdtime'],
}

projectpermfield = {
    'proj.add_project':[],
    'proj.change_project':[],
}

orgpermfield = {
    'org.add_organization':['description','investoverseasproject','orgtransactionphase','currency','decisionCycle','decisionMakingProcess','orgnameC','orgnameE','orgcode','orgtype','transactionAmountF','transactionAmountT','weChat','fundSize','address','typicalCase','fundSize_USD','transactionAmountF_USD','transactionAmountT_USD'],
    'org.adminadd_org':[],
    'org.change_organization':[],
    'org.adminchange_org':[],
}