package com.example.service;

import static com.example.util.Texts.*;
import com.example.service.impl.ListServiceImpl1;

public class OverloadService {
    public String find(int id) {
        return "User#" + id;
    }

    public String find(String id) {
        return "User#" + id;
    }

    public void process() {
        if (isEmpty("")) {
            find(1);
            find("1");
        }
        ListService svc = new ListServiceImpl1();
        svc.list();
    }
}

