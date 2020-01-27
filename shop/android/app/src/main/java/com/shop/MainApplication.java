package com.shop;

import android.app.Application;
import android.support.annotation.Nullable;

import com.facebook.react.ReactApplication;
import com.facebook.react.ReactNativeHost;
import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainReactPackage;
import com.facebook.soloader.SoLoader;
import com.reactnativenavigation.NavigationApplication;
import com.reactnativenavigation.react.NavigationReactGateway;

import java.util.Arrays;
import java.util.List;



public  class MainApplication extends NavigationApplication   {

    private List packages;

  private final ReactNativeHost mReactNativeHost = new ReactNativeHost(this) {
    @Override
    public boolean getUseDeveloperSupport() {
      return BuildConfig.DEBUG;
    }

      @Override
      public List<ReactPackage> getPackages() {
          return packages;
    }

    @Override
    protected String getJSMainModuleName() {
      return "index";
    }
  };

    @Override
  public ReactNativeHost getReactNativeHost() {
    return mReactNativeHost;
  }

    @Override
    public boolean isDebug() {
        return BuildConfig.DEBUG;
    }

    @Nullable
    @Override
    public List<ReactPackage> createAdditionalReactPackages() {
       return this.getPackages();
    }

    private  List<ReactPackage> getPackages() {
        if (packages == null) {
            packages = Arrays.<ReactPackage>asList(
                    new MainReactPackage()
            );
        }
        return packages;
    }

    @Override
  public void onCreate() {
    super.onCreate();
    SoLoader.init(this, /* native exopackage */ false);
  }
}
