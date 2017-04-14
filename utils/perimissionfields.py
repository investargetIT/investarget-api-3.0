#coding=utf-8


userpermfield = {
    'usersys.admin_changeuser':['groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','company','description','tags','email','title','gender','school','specialty','remark'],
    'usersys.trader_changeuser':['tags','company','remark','description','title','email',],
    'usersys.admin_adduser':['groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','company','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'usersys.trader_adduser':['cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','company','description','tags','email','title','gender','school','specialty','registersource','remark'],
    'changeself':['photoBucket','photoKey','cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','company','description','tags','email','title','gender'],
    'register_user':['groups','photoBucket','photoKey','cardBucket','cardKey','wechat','org','name','nameE','mobileAreaCode','mobile','company','description','tags','email','title','gender','school','specialty','registersource','remark']
}

projectpermfield = {
    'proj.add_project':[],
    'proj.change_project':[],
}

orgpermfield = {
    'org.add_organization':['description','investoverseasproject','orgtransactionphase','currency','decisionCycle','decisionMakingProcess','nameC','nameE','orgcode','orgtype','transactionAmountF','transactionAmountT','weChat','fundSize','address','typicalCase','fundSize_USD','transactionAmountF_USD','transactionAmountT_USD'],
    'org.adminadd_org':[],
    'org.change_organization':[],
    'org.adminchange_org':[],
}