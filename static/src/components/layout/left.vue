<template>
    <aside :class="asideClass">
        <nav>
            <div class="user-panel">
                <div class="pull-left image">
                  <img src="./images/boxed-bg.jpg" class="img-circle" alt="User Image">
                </div>
                <div class="pull-left info">
                  <p>{{username}}</p>
                  <a href="#"><i class="fa fa-circle text-success"></i> 在线</a>
                </div>
            </div>
            <ul class="sidebar-menu">
                <li class="header">
                    <input class="menu-filter" @keyup="filterMenu"></input>
                </li>
                <li :class="'treeview'+ isActive(treeview)" v-for="(treeview, index) in menus['treeviews']"  v-if="(treeview.url && treeview.url.length) || (treeview.items && treeview.items.length) ">
                    <a :href=" treeview.url ? '/#'+treeview.url : 'javascript:;'" @click="toogleMenu(index)">
                        <i class="fa fa-indent"></i> <span>{{ treeview.title }}</span>
                        <span class="pull-right-container" v-if="!treeview.url">
                          <i class="fa fa-angle-left pull-right"></i>
                        </span>
                    </a>
                    <transition>
                        <ul class="treeview-menu menu-open">
                            <li v-for="(menu, index2) in treeview['items']" v-show="menu['show']">
                                <a :href="(menu.url.indexOf('#') >= 0 ? menu.url : ('#' + menu.url))" @click="activeShow(index, index2)" :class="comActive(menu)"><i class='fa fa-circle-o'></i>{{menu['item_name']}}</a> 
                            </li>
                        </ul>
                    </transition>
                </li>
            </ul>
        </nav>
    </aside>
</template>
<script>
    import Ajax from 'ajax';
    let _ajax = new Ajax();
    export default {
        data(){
            return {
                asideClass: '',
                menus: {
                    title: 'Zones',
                    treeviews: [
                        /*{
                            title: '内网域名',
                            icon: 'fa-angle-left',
                            isActive: true,
                            items: [
                                { item_name: 'uuu.com',icon: 'fa-circle-o', url: "/dns/inner/uuu_com"},
                                { 'item_name': 'ooo.com',icon: 'fa-circle-o', url: "/dns/inner/uuu_com"},
                                { 'item_name': 'uuu.com',icon: 'fa-circle-o', url: "/dns/inner/uuu_com"},
                            ] 
                        }*/
                    ]
                },
                username: '',
            }
        },
        mounted(){
            let self = this;
            self.username = this.$cookies.get('dns-cookie-username');
            self.initSidebar();
        },
        methods:{
            // 初始侧边栏
            initSidebar () {
                var self = this;
                _ajax.get({
                    showLoading: false,
                    url: 'http://hfdns-test.ipo.com/page/menu_sidebar',
                    success(response){
                        self.menus.treeviews = response.data.menu;
                        // 刷新页面保留当前侧边栏选中状态
                        var mt = self.menus.treeviews.slice();
                        // 如果是首页
                        if (/#(.*)/.exec(location.href)[1] === '/') {
                            self.menus.treeviews[0].isActive = true;
                        } else {
                            self.menus.treeviews.every(function (item, index) {
                                for (var key in item) mt[index].isActive = false;
                                if ('url' in item && /#(.*)/.exec(location.href)[1] == item.url) {
                                    mt[index].isActive = true;
                                    return false;
                                } else {
                                    if (!item.url && mt[index].title == mt[localStorage.nowUrlIndex].title) {
                                        mt[localStorage.nowUrlIndex].isActive = true;
                                        if (mt[localStorage.nowUrlIndex].items[localStorage.nowUrlIndexSecond]) mt[localStorage.nowUrlIndex].items[localStorage.nowUrlIndexSecond].aActive = true;
                                        return false;
                                    }
                                }
                                return true;
                            });
                        }


                        self.menus.treeviews.forEach(function (item, index) {
                            let subMenus  = mt[index].items;
                            if(subMenus && subMenus.length > 0){
                                subMenus.forEach((menu) => {
                                    menu.show = true;
                                });
                            }
                        });


                        
                    }
                });
            },
            dosomething(){
                location.reload();
            },
            miniAside(flag){
                if(flag){
                    this.asideClass = 'aside-mini'
                } else {
                    this.asideClass = '';
                }
            },
            isActive(treeview){
                if(treeview.isActive){
                    return ' active';
                }
                return ' ';
            },
            isOpen(treeview){
                if(treeview.isActive){
                    return ' menu-open';
                }
                return ' ';
            },
            comActive (menu) {
                if(menu.aActive){
                    return ' active';
                }
                return ' ';
            },
            toogleMenu(index){
                localStorage.nowUrlIndex = index;
                localStorage.nowUrlIndexSecond = undefined;

                let tempList = this.menus.treeviews.slice();
                tempList.forEach((view, viewsIndex) => {
                    if(index != viewsIndex){
                        tempList[viewsIndex].isActive = false;
                    } else {
                        tempList[viewsIndex].isActive = tempList[viewsIndex].isActive ? false : true;
                    }
                });
                this.menus.treeviews = tempList;
            },
            filterMenu(event){
                let self = this;
                let key = event.target.value;
                let mt = self.menus.treeviews.slice();
                mt.forEach((treeview) => {
                    let menus = treeview.items;
                    if(menus && menus.length > 0){
                        menus.forEach((menu) => {
                            if(menu['item_name'].indexOf(key) >= 0 || key.length == 0){
                                menu.show = true;
                            } else {
                                menu.show = false;
                            }
                        });
                    }
                });
                self.menus.treeviews = mt;
            },
            // 当前子菜单选中高亮
            activeShow (index1, index2) {
                localStorage.nowUrlIndexSecond = index2;
                let tempList = this.menus.treeviews.slice();
                tempList.forEach(function (item, index, arr) {
                    if (!Array.isArray(item.items)) return;
                    item.items.forEach(function (listItem, listIndex, listArr) {
                        listItem.aActive = false;
                    });
                });
                tempList[index1].items.forEach(function (item, viIndex, arr) {
                    if(index2 === viIndex){
                        tempList[index1].items[viIndex].aActive = true;
                    }
                });
                this.menus.treeviews = tempList;
            }
        }
    }
</script>
<style scoped>
    aside{
        width: 230px;
        min-height: 100%;
        border-top: 0;
        border-bottom: 0;
        background-color: #222d32;
        padding-top: 51px;
        position: fixed;
        height: 100%;
        overflow-y: auto;
    }

    .aside-mini{
        width: 50px;
    }

    .dns-log-mini{
        display: none;
    }
    .dns-log{
        display: block;
    }
    .aside-mini .dns-log-mini{
        display: block;
        font-size: 16px;
    }
    .aside-mini .dns-log{
        display: none;
    }

    .user-panel>.image>img{
        border-radius: 50%;
    }
    .user-panel>.info>p{
        font-weight: bold;
        font-size: 13px;
    }
    .text-success{
        color: #2ca46a;
    }
    body .sidebar-menu li.header{
        padding-left: 0px;
        padding-right: 0px;
    }
    .menu-filter{
        background-color: #2c3b41;
        padding: 0;
        border: 0;
        border-radius: 0;
        color: #fff;
        padding: 2px;
        width: 100%;
        padding-left: 5px;

    }


    aside header{
        transition: width .3s ease-in-out;
        display: block;
        float: left;
        height: 50px;
        line-height: 50px;
        font-size: 20px;
        text-align: center;
        width: 100%;
        font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;
        font-weight: 300;
        background-color: #367fa9;
        color: #fff;
    }

    aside nav{

    }

    .sidebar-menu li.active>a>.pull-right-container>.fa-angle-left {
        -webkit-transform: rotate(-90deg);
        -ms-transform: rotate(-90deg);
        -o-transform: rotate(-90deg);
        transform: rotate(-90deg);
    }
    
    .skin-blue .sidebar-menu .treeview-menu > li > a.active{
        color: #72BFF0;
    }

</style>