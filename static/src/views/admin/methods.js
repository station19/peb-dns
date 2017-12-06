var pageNub = function (total) {
    var nub = total / 10;
    return total > 10 ? Math.floor(nub % 2 == 0 ? nub : nub + 1)  : 1;
}

export {
    pageNub
};