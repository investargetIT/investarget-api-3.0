#coding=utf-8


userpermfield = {
    'usersys.admin_changeuser':['country','userstatus','groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','remark'],
    'usersys.trader_changeuser':['tags','country','remark','description','title','email',],
    'usersys.admin_adduser':['userstatus','country','groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'usersys.trader_adduser':['cardBucket','cardKey','country','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'changeself':['photoBucket','photoKey','country','cardBucket','cardKey','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender'],
    'register_user':['groups','photoBucket','photoKey','country','cardBucket','cardKey','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'usersys.admin_changefriend':[],


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