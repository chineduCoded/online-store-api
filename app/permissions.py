from enum import Enum

class PermissionsType(str, Enum):
    """Granular permissions for different resources"""
    # Product permissions
    PRODUCT_READ = "product:read"
    PRODUCT_WRITE = "product:write"
    PRODUCT_DELETE = "product:delete"
    PRODUCT_MANAGE_VARIANTS = "product:manage_variants"
    PRODUCT_MANAGE_IMAGES = "product:manage_images"
    PRODUCT_MANAGE_INVENTORY = "product:manage_inventory"

    # Category permissions
    CATEGORY_READ = "category:read"
    CATEGORY_WRITE = "category:write"
    CATEGORY_DELETE = "category:delete"
    CATEGORY_ANALYTICS = "category:analytics"
    CATEGORY_IMPORT = "category:import"
    CATEGORY_EXPORT = "category:export"
    CATEGORY_MANAGE_HIERARCHY = "category:manage_hierarchy"

    # Order permissions
    ORDER_READ = "order:read"
    ORDER_MANAGE = "order:manage"
    ORDER_UPDATE_STATUS = "order:update_status"
    ORDER_MANAGE_ITEMS = "order:manage_items"
    
    # User Permissions
    USER_READ = "user:read"
    USER_MANAGE = "user:manage"
    USER_MANAGE_ROLES = "user:manage_roles"
    
    # Payment Permissions
    PAYMENT_READ = "payment:read"
    PAYMENT_PROCESS = "payment:process"
    PAYMENT_REFUND = "payment:refund"
    PAYMENT_ANALYTICS = "payment:analytics"
    PAYMENT_AUDIT = "payment:audit"
    PAYMENT_EXPORT = "payment:export"
    PAYMENT_VIEW_SENSITIVE = "payment:view_sensitive"
    
    # Special Operations
    DISCOUNT_MANAGE = "discount:manage"
    REPORT_GENERATE = "report:generate"
    REPORT_SCHEDULE = "report:schedule"
    REPORT_TEMPLATE = "report:template"
    REPORT_EXPORT = "report:export"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_SHARE = "analytics:share"
    ANALYTICS_CUSTOMIZE = "analytics:customize"
    ANALYTICS_VIEW = "analytics:view"

class RoleType(str, Enum):
    """Predefined roles with default permissions"""
    SUPER_ADMIN = "super_admin"
    STORE_MANAGER = "store_manager"
    SUPPORT_STAFF = "support_staff"
    CUSTOMER = "customer"

DEFAULT_ROLE_PERMISSIONS = {
    RoleType.SUPER_ADMIN: [
        # Product
        PermissionsType.PRODUCT_READ,
        PermissionsType.PRODUCT_WRITE,
        PermissionsType.PRODUCT_DELETE,
        PermissionsType.PRODUCT_MANAGE_VARIANTS,
        PermissionsType.PRODUCT_MANAGE_IMAGES,
        PermissionsType.PRODUCT_MANAGE_INVENTORY,
        
        # Category
        PermissionsType.CATEGORY_READ,
        PermissionsType.CATEGORY_WRITE,
        PermissionsType.CATEGORY_DELETE,
        PermissionsType.CATEGORY_MANAGE_HIERARCHY,
        
        # Order
        PermissionsType.ORDER_READ,
        PermissionsType.ORDER_MANAGE,
        PermissionsType.ORDER_UPDATE_STATUS,
        PermissionsType.ORDER_MANAGE_ITEMS,
        
        # User
        PermissionsType.USER_READ,
        PermissionsType.USER_MANAGE,
        PermissionsType.USER_MANAGE_ROLES,
        
        # Payment
        PermissionsType.PAYMENT_READ,
        PermissionsType.PAYMENT_PROCESS,
        PermissionsType.PAYMENT_REFUND,
        PermissionsType.PAYMENT_VIEW_SENSITIVE
    ],
    RoleType.STORE_MANAGER: [
        # Product
        PermissionsType.PRODUCT_READ,
        PermissionsType.PRODUCT_WRITE,
        PermissionsType.PRODUCT_MANAGE_VARIANTS,
        PermissionsType.PRODUCT_MANAGE_IMAGES,
        PermissionsType.PRODUCT_MANAGE_INVENTORY,
        
        # Category
        PermissionsType.CATEGORY_READ,
        PermissionsType.CATEGORY_WRITE,
        
        # Order
        PermissionsType.ORDER_READ,
        PermissionsType.ORDER_UPDATE_STATUS,
        PermissionsType.ORDER_MANAGE_ITEMS,
        
        # Payment
        PermissionsType.PAYMENT_READ
    ],
    RoleType.SUPPORT_STAFF: [
        PermissionsType.ORDER_READ,
        PermissionsType.ORDER_UPDATE_STATUS,
        PermissionsType.USER_READ,
        PermissionsType.PAYMENT_READ
    ],
    RoleType.CUSTOMER: [
        PermissionsType.ORDER_READ,
        PermissionsType.PAYMENT_READ,
        # Limited product access
        PermissionsType.PRODUCT_READ
    ]
}
    