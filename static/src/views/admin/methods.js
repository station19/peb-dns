
import _ from '../../components/fn/tool';
function searchData(str, index) {
    var reqData = {};
    switch (str) {
    case 'searchUserData' : 
        for (var key in this.searchUserData) {
            reqData[key] = this.searchUserData[key].value;
        }
        reqData = _.compact(reqData);
        this.fetchUser(this, Object.assign(reqData, {
            currentPage : index || 1
        }), 'http://hfdns-test.ipo.com/admin/users');
        break;
    case 'searchRoleData' :
        for (var key in this.searchRoleData) {
            reqData[key] = this.searchRoleData[key].value;
        }
        reqData = _.compact(reqData);
        this.roleAjax(this, Object.assign(reqData, {
            currentPage : index || 1
        }), 'http://hfdns-test.ipo.com/admin/roles', function () {
            if (!this.editUserVal.role) return;
            var arr = JSON.parse('[' + this.editUserVal.role + ']');
            for (let key in this.tableRoleData) {
                if (arr.indexOf(this.tableRoleData[key].id) != -1) {
                    this.tableRoleData[key].isDanger = 'danger';    
                } else {
                    this.tableRoleData[key].isDanger = '';
                }
            }
        }.bind(this));
        break;
    case 'searchPrivilegeData' :
        for (var key in this.searchPrivilegeData) {
            reqData[key] = this.searchPrivilegeData[key].value + '';
        }
        reqData = _.compact(reqData);
        this.privilegeAjax(this, Object.assign(reqData, {
            currentPage : index || 1
        }), 'http://hfdns-test.ipo.com/admin/privileges', function () {
            // 显示关联状态
            if (!this.editRoleVal.privilege) return;
            var arr = JSON.parse('[' + this.editRoleVal.privilege + ']');

            for (let key in this.tablePrivilegeData) {
                if (arr.indexOf(this.tablePrivilegeData[key].id) != -1) {
                    this.tablePrivilegeData[key].isDanger = 'danger';    
                } else {
                    this.tablePrivilegeData[key].isDanger = '';
                }
            }
            this.editRoleVal.privilege = '';
        }.bind(this));
        break;
    }
}

function relation (index, id, item) {
    switch (index) {
    case 0 : 
        // 用户编辑
        // 添加还是删除
        var arr = JSON.parse('[' + this.editUserVal.role + ']');

        var arrName = [];
        this.editUserVal.roleName && arrName.push(this.editUserVal.roleName.split(','));
        arrName = _.flatten(arrName);
        if (arr.indexOf(id) != -1) {
            var idx = arr.indexOf(id);
            arr.splice(idx, 1);
            arrName.splice(idx, 1);
            item.isDanger = '';
        } else {
            arr.push(id);
            arrName.push(item.name);
            item.isDanger = 'danger';
        }
        this.editUserVal.role = arr.join(',');
        arrName.forEach((item, index, arr) => {
            if (!index) return;
            if (/\n/.test(item)) return;
            arrName[index] = '\n' + item;
        });
        this.editUserVal.roleName = arrName.join(',');
        break ;
    case 1 : 
        // 角色编辑
        // 添加还是删除
        var arr = JSON.parse('[' + this.editRoleVal.privilege + ']');
        var arrName = [];
        arrName.push(this.editRoleVal.privilegeName.split(','));
        arrName = _.flatten(arrName);
        if (arr.indexOf(id) != -1) {
            var idx = arr.indexOf(id);
            arr.splice(idx, 1);
            arrName.splice(idx, 1);
            item.isDanger = '';
        } else {
            arr.push(id);
            arrName.push(item.name);
            item.isDanger = 'danger';
        }
        arrName.forEach((item, index, arr) => {
            if (!index) return;
            if (/\n/.test(item)) return;
            arrName[index] = '\n' + item;
        });
        this.editRoleVal.privilege = arr.join(',');
        this.editRoleVal.privilegeName = arrName.join(',');
        break ;
    case 2 :
        // 权限
        // 添加角色对话框关联权限
        var arr = !this.newRole.privilege_ids ? [] : this.newRole.privilege_ids.split(',');
        var arrName = [];
        this.newRole.privilege_idsName && arrName.push(this.newRole.privilege_idsName.split(','));
        arrName = _.flatten(arrName);
        if (arr.indexOf(id + '') != -1) {
            var idx = arr.indexOf(id + '');
            arr.splice(idx, 1);
            arrName.splice(idx, 1);
            item.isDanger = '';
        } else {
            arr.push(id);
            arrName.push(item.name);
            item.isDanger = 'danger';
        }
        arrName.forEach((item, index, arr) => {
            if (!index) return;
            if (/\n/.test(item)) return;
            arrName[index] = '\n' + item;
        });
        this.newRole.privilege_ids = arr.join(',');
        this.newRole.privilege_idsName = arrName.join(',');
        break ;
    }
}

function pageNub (total) {
    var nub = total / 10;
    return total > 10 ? Math.floor(nub % 2 == 0 ? nub : nub + 1)  : 1;
}

export {
    searchData,
    relation,
    pageNub
};