
define(['underscore'], function(_) {

    PrairieRole = {};

    /** All roles, ordered from most permissions to least.
     */
    PrairieRole.roleList = ['Superuser', 'Instructor', 'TA', 'Student'];

    /** Integer ranks of roles, must be index in roleList array.
     */
    PrairieRole.SUPERUSER = 0;
    PrairieRole.INSTRUCTOR = 1;
    PrairieRole.TA = 2;
    PrairieRole.STUDENT = 3;

    /** Convert role to integer rank.

        @param {String} role Role to convert (e.g., 'Superuser', 'Instructor', etc).
        @return {number} Integer rank of the role.
    */
    PrairieRole.roleToRank = function(role) {
        var rank = _(this.roleList).indexOf(role);
        if (rank < 0) {
            rank = this.roleToRank(this.leastPermissiveRole());
        }
        return rank;
    };
    
    /** Convert integer rank to role.

        @param {number} rank Integer rank of the role.
        @return {String} Role (e.g., 'Superuser', 'Instructor', etc).
    */
    PrairieRole.rankToRole = function(rank) {
        var role;
        // make sure rank is an integer and an valid index
        if (!isNaN(rank) && (rank | 0 === rank) && rank >= 0 && rank < this.roleList.length) {
            role = this.roleList[rank];
        } else {
            role = this.leastPermissiveRole();
        }
        return role;
    };
    
    /** Return the least permissive of the two given roles.

        @param {String} role1 Name of the first role (e.g., 'Superuser', 'Instructor', etc).
        @param {String} role2 Name of the second role.
        @return {String} The least permissive of the two roles.
    */
    PrairieRole.leastPermissive = function(role1, role2) {
        var rank1 = this.roleToRank(role1);
        var rank2 = this.roleToRank(role2);
        var rank = Math.max(rank1, rank2);
        var role = this.rankToRole(rank);
        return role;
    };

    /** Whether the given role is a known role.

        @param {String} role Role to test for validity.
        @return {Boolean} Whether role is valid.
    */
    PrairieRole.isRoleValid = function (role) {
        return _(this.roleList).contains(role);
    };
    
    /** Return the least permissive role.

        @return {String} The least permissive role.
    */
    PrairieRole.leastPermissiveRole = function () {
        return this.roleList[this.roleList.length - 1];
    };
    
    /** Return list of roles that are no more permissive than the given role.

        @param {String} role The base role.
        @return {Array} List of roles that are equal-or-less permissive than role.
    */
    PrairieRole.availableRoles = function(role) {
        var rank = this.roleToRank(role);
        return _(this.roleList).rest(rank);
    };
    
    /** Test whether a role has permission to conduct the given operation.

        @param {String} role Role to test (e.g., 'Superuser', 'Instructor', etc).
        @param {String} operation Name of the operation (e.g., 'overrideScore', 'seeQID', etc).
        @return {Boolean} Whether the role has permission to conduct the operation.
    */
    PrairieRole.hasPermission = function(role, operation) {
        var rank = this.roleToRank(role);
        var permission = false;
        if (operation === 'overrideScore' && rank <= this.INSTRUCTOR)
            permission = true;
        if (operation === 'overrideVID' && rank <= this.TA)
            permission = true;
        if (operation === 'seeQID' && rank <= this.TA)
            permission = true;
        if (operation === 'changeUser' && rank <= this.TA)
            permission = true;
        if (operation === 'changeMode' && rank <= this.INSTRUCTOR)
            permission = true;
        if (operation === 'seeAvailDate' && rank <= this.TA)
            permission = true;
        if (operation === 'bypassAvailDate' && rank <= this.TA)
            permission = true;
        return permission;
    };

    return PrairieRole;
});
