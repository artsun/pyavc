# pyavc  
SELinux log AVC denials parser. Make source policy files  

## Usage
1)  Get current SELinux denials using:
	```
	> tail -f /var/log/messages | grep AVC
	```
	```
	type=AVC msg=audit(1601453275.017:543117): avc:  denied  { siginh } for  pid=11670 comm="pkla-check-auth" scontext=system_u:system_r:policykit_t:s0 tcontext=system_u:system_r:policykit_auth_t:s0 tclass=process permissive=1
	```
2)  To get **require** and **allow**s from logs/avc file:  
	```  
	 > python3 genavc.py -f logs/avc 
	```
	 #### output:
	```
	require {
	type init_t;
	type sshd_t;
	type chkpwd_t;
	type policykit_t;
	type unconfined_t;
	type system_dbusd_t;
	type policykit_auth_t;
	type setroubleshootd_t;
	type systemd_tmpfiles_t;

	class capability {net_admin};
	class process {siginh};
	class process {siginh rlimitinh noatsecure};
	}

	allow sshd_t chkpwd_t: process {siginh rlimitinh noatsecure};
	allow init_t unconfined_t: process {siginh};
	allow system_dbusd_t system_dbusd_t: capability {net_admin};
	allow systemd_tmpfiles_t systemd_tmpfiles_t: capability {net_admin};
	allow init_t chkpwd_t: process {siginh};
	allow policykit_t policykit_auth_t: process {siginh rlimitinh noatsecure};
	allow system_dbusd_t setroubleshootd_t: process {siginh rlimitinh noatsecure};
	```
## Extras
- to get simple policy file specify name without extension:
	```
	> python3 genavc.py -f logs/avc -te policy_filename
	```
 - to see avc tree (verbose) with **source_context -> target_context class { permissions }**:
	```
	> python3 genavc.py -f logs/avc -v
	```
	```
	systemd_tmpfiles_t
	        -> systemd_tmpfiles_t
	                        -> capability {net_admin}
	system_dbusd_t
	        -> system_dbusd_t
	                        -> capability {net_admin}
	        -> setroubleshootd_t
	                        -> process {noatsecure rlimitinh siginh}
	sshd_t
	        -> chkpwd_t
	                        -> process {noatsecure rlimitinh siginh}
	policykit_t
	        -> policykit_auth_t
	                        -> process {noatsecure rlimitinh siginh}
	init_t
	        -> chkpwd_t
	                        -> process {siginh}
	        -> unconfined_t
	                        -> process {siginh}

	```
