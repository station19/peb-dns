import Vue from 'vue';
import Router from 'vue-router';
import index from '@/views/index/page.vue';
import optLogs from '@/views/logs.vue';
import domain from '@/views/domainmanager.vue';
import zones from '@/views/zone.vue';
import views from '@/views/view.vue';
import servers from '@/views/dnsserver.vue';
import userAdmin from '@/views/admin/user.vue';
import roleAdmin from '@/views/admin/role.vue';
import privilegeAdmin from '@/views/admin/privilege.vue';
import userConfig from '@/views/userconfig.vue';

Vue.use(Router)

let routerInstance = new Router({
    routes: [
        {
            path: '/',name: 'index',component: index
        },{
            path: '/dns/logs',name: 'logs',component: optLogs
        },{
            path: '/dns/records/zoneId/:zoneId',name: 'domain', component: domain
        },{
            path: '/dns/zones', name: 'zones', component: zones
        },{
            path: '/dns/views', name: 'views', component: views
        },{
            path: '/dns/servers', name: 'servers', component: servers
        },{
            path: '/admin/users', name: 'userAdmin', component: userAdmin
        },{
            path: '/admin/roles', name: 'roleAdmin', component: roleAdmin
        },{
            path: '/admin/privileges', name: 'privilegeAdmin', component: privilegeAdmin
        },{
            path: '/dns/userConfig', name: 'userConfig', component: userConfig
        },
    ]
});




export default routerInstance;
