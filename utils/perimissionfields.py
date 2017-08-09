#coding=utf-8


userpermfield = {
    'usersys.admin_changeuser':['IR','targetdemand','mergedynamic','ishasfundorplan','department','lastmodifytime','orgarea','lastmodifyuser','country','userstatus','groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','remark'],
    'usersys.trader_changeuser':['lastmodifyuser','targetdemand','mergedynamic','department','ishasfundorplan','lastmodifytime','orgarea','tags','country','remark','description','title','email',],
    'usersys.admin_adduser':['IR','targetdemand','mergedynamic','ishasfundorplan','userstatus','department','country','groups','photoBucket','orgarea','photoKey','cardBucket','cardKey','wechat','org','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'usersys.trader_adduser':['cardBucket','targetdemand','mergedynamic','ishasfundorplan','cardKey','department','country','wechat','org','orgarea','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'changeself':['photoBucket','photoKey','targetdemand','mergedynamic','ishasfundorplan','country','cardBucket','department','cardKey','wechat','org','orgarea','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender'],
    'register_user':['groups','targetdemand','mergedynamic','ishasfundorplan','photoBucket','photoKey','country','cardBucket','department','cardKey','wechat','org','orgarea','usernameC','usernameE','mobileAreaCode','mobile','description','tags','email','title','gender','school','specialty','registersource','remark'],
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