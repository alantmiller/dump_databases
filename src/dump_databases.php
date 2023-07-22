<?php
/**
 * @author Alan T. Miller <alan@alanmiller.com>
 * @copyright Copyright (C) 2010, Alan T Miller, All Rights Reserved.
 *
 * Sample Usage:
 *
 * require_once('class.dump.databases.cli.php');
 * $obj = new dump_databases;
 * $obj->setDumpDir('/var/var/datadumps');
 * $obj->setDumpCmd('/usr/bin/mysqldump');
 * $obj->setAdminEmail('admin@foo.com');
 * $obj->setFromEmail('computer@foo.com');
 * $obj->setOwner('apache');
 * $obj->setGroup('apache');
 * $obj->addDatabase(new database('foodb','username','password'));
 * $obj->addDatabase(new database('bardb','username','password'));
 * $obj->process();
 *
 */
class database
{
    public $database;
    public $username;
    public $password;

    public function __construct($database, $username, $password)
    {
        $this->database = trim($database);
        $this->username = trim($username);
        $this->password = trim($password);
    }
}

class dump_databases
{
    private $cmd_tar;
    private $cmd_dump;
    private $dump_dir;
    private $owner;
    private $group;
    private $email_from;
    private $email_admin;
    private $dump_options;
    private $databases = array();
    private $msgs = array();
    private $host;

    public function __construct()
    {
        $options = array(
        'opt' => true,
        'skip-extended-insert' => true,
        'comments' => true,
        'order-by-primary' => true,
        'routines' => true,
        'triggers' => true,
        'complete-insert' => true
        );

        array_push($this->msgs,sprintf('STARTED @ %s', date("F j, Y, g:i a")));

        $this->cmd_tar   = trim(`which tar`);
        $this->cmd_dump  = trim(`which mysqldump`);

        foreach ($options AS $key => $val) {
            if ($val == true) {
                $this->dump_options .= sprintf('--%s ', $key);
            }
        }
        $this->dump_options = substr($this->dump_options,0,-1);
    }

    public function addDatabase(database $obj)
    {
        $obj->database = trim($obj->database);
        $obj->username = trim($obj->username);
        $obj->password = trim($obj->password);
        array_push($this->databases,$obj);
        array_push($this->msgs,sprintf('ADDED DATABASE: %s',$obj->database));
        return $this;
    }

    public function setDumpDir($str)
    {
        $str = trim($str);
        // clean trailing slash if exists
        if (substr($str,-1) == '/') {
            $str = substr($str, 0, -1);
        }
        $this->dump_dir = $str;
        return $this;
    }

    public function setDumpCmd($str)
    {
        $this->cmd_dump = quotemeta(trim($str));
        return $this;
    }

    public function setOwner($str)
    {
        $this->owner = trim($str);
        return $this;
    }

    public function setGroup($str)
    {
        $this->group = trim($str);
        return $this;
    }

    public function setAdminEmail($str)
    {
        $this->email_admin = trim($str);
        return $this;
    }

    public function setFromEmail($str)
    {
        $this->email_from = trim($str);
        return $this;
    }

    public function setEmailSubject($str) {
        $this->email_subject = trim($str);
        return $this;
    }

    public function setHost($str) 
    { 
        $this->host = trim($str);
        return $this;
    }

    public function getMessages()
    {
        return implode("\n", $this->msgs)."\n";
        return $this;
    }

    public function process()
    {
        $this->_sanityCheck()
        ->_dump()
        ->_cleanGarbage()
        ->_sendNotice();

        return $this;
    }

    private function _dump()
    {
        print("dumping databases...\n");
        foreach ($this->databases AS $db)
        {
            $file = sprintf('%s/%s.%s.sql.tar.gz',$this->dump_dir, date('Y-m-d'), $db->database);
            $sqlfile = sprintf('%s/%s.%s.sql',$this->dump_dir, date('Y-m-d'),$db->database);

            // remove old file if exist
            if (file_exists($file) && is_writable($file)) {
                unlink($file);
                array_push($this->msgs,sprintf('REMOVED FILE: %s',$file));
            }

            // remove old sql file if exists
            if (file_exists($sqlfile) && is_writable($sqlfile)) {
                unlink($sqlfile);
                array_push($this->msgs,sprintf('REMOVED FILE: %s',$sqlfile));
            }

            // build command
            
            if ($this->host != '') {
                $cmd = sprintf("%s --user=%s --password='%s' --host=%s %s %s > %s",
                $this->cmd_dump,
                $db->username,
                $db->password,
                $this->host,
                $this->dump_options,
                $db->database,
                $sqlfile);
            } else {
                $cmd = sprintf("%s --user=%s --password='%s' %s %s > %s",
                $this->cmd_dump,
                $db->username,
                $db->password,
                $this->dump_options,
                $db->database,
                $sqlfile);
            }

            // execute dump
            exec($cmd);


            // print out a status update
            print('dumping database: '.$db->database.'...'."\n");
            array_push($this->msgs,sprintf('DUMPED DATABASE: %s',$db->database));

            // create a tarball
            if (file_exists($sqlfile) && is_writable($sqlfile)) {
                $cmd = sprintf("%s cfzP %s %s", $this->cmd_tar, $file, $sqlfile);
                array_push($this->msgs,sprintf('COMPRESSED: %s',$sqlfile));
                exec($cmd);
            }

            // change owner
            if (file_exists($file) && is_writable($file)) {
                chown($file, $this->owner);
                array_push($this->msgs,sprintf('CHANGED OWNER ON: %s to %s',$file, $this->owner));
            }

            // change group
            if (file_exists($file) && is_writable($file)) {
                chgrp($file, $this->group);
                array_push($this->msgs,sprintf('CHANGED GROUP ON: %s to %s',$file, $this->group));
            }

            // delete temp sql file
            if (file_exists($sqlfile) && is_writable($sqlfile)) {
                unlink($sqlfile);
                array_push($this->msgs,sprintf('REMOVED FILE: %s',$sqlfile));
            }
        }

        print('dumping complete! '."\n");
        return $this;
    }

    private function _sanityCheck()
    {
        print('sanity check...'."\n");
        // check to make sure dump command is defined
        if (!strlen($this->cmd_dump) > 0) {
            exit('SANITY CHECK FAILED: dump command not defined'."\n");
        } else {
            array_push($this->msgs,sprintf('COMMAND SET: %s',$this->cmd_dump));
        }

        // check to make sure dump command is correct
        if (substr(trim($this->cmd_dump),-9) != 'mysqldump') {
            exit('SANITY CHECK FAILED: dump command not correct'."\n");
        } else {
            array_push($this->msgs,sprintf('COMMAND CHECKED OUT: %s',$this->cmd_dump));
        }

        // check to make sure tar command is defined
        if (!strlen($this->cmd_tar) > 0) {
            exit('SANITY CHECK FAILED: tar command not defined'."\n");
        } else {
            array_push($this->msgs,sprintf('COMMAND SET: %s',$this->cmd_tar));
        }

        // check to make sure tar command is correct
        if (substr(trim($this->cmd_tar),-3) != 'tar') {
            exit('SANITY CHECK FAILED: tar command not correct'."\n");
        } else {
            array_push($this->msgs,sprintf('COMMAND CHECKED OUT: %s',$this->cmd_tar));
        }

        // check to make sure dump directory is valid
        if (!is_dir($this->dump_dir)) {
            $str = 'SANITY CHECK FAILED: dump_dir does not exist: %s'."\n";
            exit(sprintf($str,$this->dump_dir));
        } else {
            array_push($this->msgs,sprintf('DUMP DIR CHECKED OUT: %s',$this->dump_dir));
        }

        // check if dump dir is writable
        if (!is_writable($this->dump_dir)) {
            $str = 'SANITY CHECK FAILED: dump_dir not writable by %s: %s'."\n";
            exit(sprintf($str,$this->owner, $this->dump_dir));
        } else {
            array_push($this->msgs,sprintf('DUMP DIR WRITEABLE: %s',$this->dump_dir));
        }

        // Check email_from
        if (!filter_var($this->email_from, FILTER_VALIDATE_EMAIL)) {
            $str = 'SANITY CHECK FAILED: From email appears to be invalid: %s'."\n";
            exit(sprintf($str,$this->email_from));
        } else {
            array_push($this->msgs,sprintf('EMAIL FROM CHECKED OUT: %s',$this->email_from));
        }

        // Check email_admin
        if (!filter_var($this->email_admin, FILTER_VALIDATE_EMAIL)) {
            $str = 'SANITY CHECK FAILED: Admin email appears to be invalid: %s'."\n";
            exit(sprintf($str,$this->email_admin));
        } else {
            array_push($this->msgs,sprintf('EMAIL ADMIN CHECKED OUT: %s',$this->email_admin));
        }

        // check to make sure group is set
        // and set root as default if not
        if (!isset($this->group)) {
            $this->group = 'root';
            array_push($this->msgs,'SET GROUP TO ROOT');
        }

        // check to make sure owner is set
        // and set root as default if not
        if (!isset($this->owner)) {
            $this->owner = 'root';
            array_push($this->msgs,'SET OWNER TO ROOT');
        }

        array_push($this->msgs, 'SANITY CHECKS PASSED');
        print('sanity check passed!'."\n");
        return $this;
    }

    private function _cleanGarbage()
    {
        print('cleaning garbage...'."\n");
        array_push($this->msgs,'CLEANING GARBAGE');
        foreach(new DirectoryIterator($this->dump_dir) AS $file ){
            if(!$file->isDot() && !$file->isDir()) {
                $timeinterval = strtotime('-1 week',time());
                $maxtime = (time() - $timeinterval);
                if ((time() - $file->getCTime()) > $maxtime) {
                    unlink(sprintf('%s/%s',$this->dump_dir,$file->getFilename()));
                    array_push($this->msgs,sprintf('DELETED: %s', $file->getFilename()));
                } else {
                    array_push($this->msgs,sprintf('LEFT FILE: %s', $file->getFilename()));
                }
            }
        }
        print('cleaning garbage complete!'."\n");
        return $this;
    }

    private function _sendNotice()
    {
        print('sending notice...'."\n");
        array_push($this->msgs,sprintf('SENT EMAIL NOTIFICATION: %s',time()));
        if (strlen($this->email_subject) > 0) {
            $subject = sprintf('DATABASE DUMP COMPLETE (%s) @ %s',$this->email_subject, date("F j, Y, g:i a"));
        } else {
            $subject = sprintf('DATABASE DUMP COMPLETE @ %s',date("F j, Y, g:i a"));
        }
        $message = sprintf('%s' ."\n %s", $subject, $this->getMessages());
        $format = "From: %s\r\nReply-To: %s\r\nX-Mailer: PHP/%s\r\n";
        $headers = sprintf($format, $this->email_from,$this->email_from,phpversion());
        if (!mail($this->email_admin, $subject, $message, $headers)) {
            exit('ERROR SENDING MAIL'."\n");
        }
        print('sending notice complete!'."\n");
        return $this;
    }
}
