.class public Llocal/rover/usbtether/EnableReceiver;
.super Landroid/content/BroadcastReceiver;

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V
    return-void
.end method

.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 10
    const-string v9, "RoverUsbLink"
    :try_start
    invoke-virtual {p2}, Landroid/content/Intent;->getAction()Ljava/lang/String;
    move-result-object v0
    const-string v1, "android.hardware.usb.action.USB_STATE"
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :check_tether
    const-string v1, "connected"
    const/4 v2, 0x0
    invoke-virtual {p2, v1, v2}, Landroid/content/Intent;->getBooleanExtra(Ljava/lang/String;Z)Z
    move-result v1
    if-eqz v1, :done

    :check_tether
    const-string v0, "connectivity"
    invoke-virtual {p1, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v0
    const-class v1, Landroid/net/ConnectivityManager;
    const-string v2, "getTetheredIfaces"
    const/4 v3, 0x0
    new-array v3, v3, [Ljava/lang/Class;
    invoke-virtual {v1, v2, v3}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;
    move-result-object v2
    const/4 v3, 0x0
    new-array v3, v3, [Ljava/lang/Object;
    invoke-virtual {v2, v0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, [Ljava/lang/String;
    if-eqz v2, :enable
    array-length v3, v2
    const/4 v4, 0x0
    :interface_loop
    if-ge v4, v3, :enable
    aget-object v5, v2, v4
    const-string v6, "rndis"
    invoke-virtual {v5, v6}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :already_enabled
    const-string v6, "usb"
    invoke-virtual {v5, v6}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :already_enabled
    add-int/lit8 v4, v4, 0x1
    goto :interface_loop

    :enable
    invoke-static {v0}, Llocal/rover/usbtether/EnableReceiver;->tetherAvailable(Ljava/lang/Object;)Z
    move-result v2
    if-nez v2, :done
    const-string v2, "setUsbTethering"
    const/4 v3, 0x1
    new-array v3, v3, [Ljava/lang/Class;
    sget-object v4, Ljava/lang/Boolean;->TYPE:Ljava/lang/Class;
    const/4 v5, 0x0
    aput-object v4, v3, v5
    invoke-virtual {v1, v2, v3}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;
    move-result-object v2
    const/4 v3, 0x1
    new-array v3, v3, [Ljava/lang/Object;
    sget-object v4, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    aput-object v4, v3, v5
    invoke-virtual {v2, v0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v2
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string v5, "setUsbTethering(true) result="
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v9, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :done

    :already_enabled
    const-string v0, "USB tethering already enabled"
    invoke-static {v9, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end
    .catch Ljava/lang/Exception; {:try_start .. :try_end} :error
    goto :done
    :error
    move-exception v0
    const-string v1, "Unable to enable USB tethering"
    invoke-static {v9, v1, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :done
    return-void
.end method

.method private static tetherAvailable(Ljava/lang/Object;)Z
    .locals 9
    const-class v0, Landroid/net/ConnectivityManager;
    const-string v1, "getTetherableIfaces"
    const/4 v2, 0x0
    new-array v2, v2, [Ljava/lang/Class;
    invoke-virtual {v0, v1, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;
    move-result-object v1
    const/4 v2, 0x0
    new-array v2, v2, [Ljava/lang/Object;
    invoke-virtual {v1, p0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, [Ljava/lang/String;
    if-eqz v2, :unavailable
    array-length v3, v2
    const/4 v4, 0x0
    :loop
    if-ge v4, v3, :unavailable
    aget-object v5, v2, v4
    const-string v6, "rndis"
    invoke-virtual {v5, v6}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :tether
    const-string v6, "usb"
    invoke-virtual {v5, v6}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :tether
    add-int/lit8 v4, v4, 0x1
    goto :loop
    :tether
    const-string v1, "tether"
    const/4 v2, 0x1
    new-array v2, v2, [Ljava/lang/Class;
    const-class v3, Ljava/lang/String;
    const/4 v4, 0x0
    aput-object v3, v2, v4
    invoke-virtual {v0, v1, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;
    move-result-object v1
    const/4 v2, 0x1
    new-array v2, v2, [Ljava/lang/Object;
    aput-object v5, v2, v4
    invoke-virtual {v1, p0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Integer;
    invoke-virtual {v1}, Ljava/lang/Integer;->intValue()I
    move-result v2
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "tether USB interface result="
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
    const-string v4, "RoverUsbLink"
    invoke-static {v4, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    if-nez v2, :unavailable
    const/4 v0, 0x1
    return v0
    :unavailable
    const/4 v0, 0x0
    return v0
.end method
